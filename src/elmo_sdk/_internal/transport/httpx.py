from __future__ import annotations

import contextlib
import threading
import time
from collections.abc import AsyncGenerator, Awaitable, Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, cast
from urllib.parse import unquote_plus, urlsplit

from ..core.backoff import TIMER_LIMIT
from ..core.errors import (
    TransportError,
    safe_address,
    timeout_error,
    unsendable_address,
)
from ..core.types import PlacedCredential, PreparedRequest, RawResponse, StreamResponse


class HttpxResponse(RawResponse, StreamResponse, Protocol): ...


class HttpxLike(Protocol):
    """The part of an httpx client this SDK calls."""

    def build_request(
        self,
        method: str,
        url: str,
        *,
        content: bytes | None = None,
        headers: list[tuple[bytes, bytes]] | None = None,
        timeout: Any = None,
    ) -> Any: ...

    def close(self) -> None: ...

    def send(
        self,
        request: Any,
        *,
        stream: bool = False,
        auth: Any = None,
        follow_redirects: Any = None,
    ) -> HttpxResponse: ...


def _limit(request: PreparedRequest) -> float | None:
    limit = request.options.get("timeout")
    if isinstance(limit, bool) or not isinstance(limit, (int, float)) or limit <= 0:
        return None
    return min(float(limit), TIMER_LIMIT)


def _read_by(
    response: HttpxResponse, deadline: float, request: PreparedRequest
) -> HttpxResponse:
    parts: list[bytes] = []
    try:
        for part in response.iter_bytes():
            if time.monotonic() > deadline:
                raise timeout_error(request)
            parts.append(part)
        if time.monotonic() > deadline:
            raise timeout_error(request)
    except BaseException:
        response.close()
        raise
    cast(Any, response)._content = b"".join(parts)
    return response


class AsyncHttpxResponse(RawResponse, Protocol): ...


class AsyncHttpxLike(Protocol):
    """The part of an async httpx client this SDK calls."""

    def aclose(self) -> Awaitable[None]: ...

    @property
    def is_closed(self) -> bool: ...

    def build_request(
        self,
        method: str,
        url: str,
        *,
        content: bytes | None = None,
        headers: list[tuple[bytes, bytes]] | None = None,
        timeout: Any = None,
    ) -> Any: ...

    def send(
        self,
        request: Any,
        *,
        stream: bool = False,
        auth: Any = None,
        follow_redirects: Any = None,
    ) -> Awaitable[AsyncHttpxResponse]: ...


def _name(pair: str) -> str:
    return unquote_plus(pair.partition("=")[0])


def _pairs(query: str) -> list[str]:
    return [pair for pair in query.split("&") if pair]


def httpx_options(request: PreparedRequest) -> dict[str, Any]:
    options: dict[str, Any] = {
        "content": request.body,
        "headers": [
            (name.encode("latin-1"), value.encode("latin-1"))
            for name, value in request.meta.items()
        ],
        "method": (request.operation.method or "get").upper(),
        "url": request.address,
    }
    timeout = request.options.get("timeout")
    if isinstance(timeout, (int, float)):
        options["timeout"] = min(timeout, TIMER_LIMIT) if timeout else None
    elif timeout is not None:
        options["timeout"] = timeout
    return options


def build_httpx_request(
    client: HttpxLike | AsyncHttpxLike, request: PreparedRequest
) -> Any:
    built = client.build_request(**httpx_options(request))
    _, _, ours = request.address.partition("?")
    sent = built.url.query.decode("ascii")
    if sent == ours:
        return built
    names = {_name(pair) for pair in _pairs(ours)}
    theirs = [pair for pair in _pairs(sent) if _name(pair) not in names]
    query = "&".join(_pairs(ours) + theirs)
    built.url = built.url.copy_with(query=query.encode("ascii") if query else None)
    return built


def check_address(address: str) -> None:
    shown = safe_address(address)
    try:
        parts = urlsplit(address)
    except ValueError:
        parts = urlsplit("")
    if parts.scheme in ("http", "https") and parts.netloc:
        return
    if parts.scheme and parts.scheme not in ("http", "https"):
        raise unsendable_address(
            shown,
            f"uses `{parts.scheme}:`, which this client does not send",
            "Start the base URL with `https://`.",
        )
    raise unsendable_address(
        shown, "is not a full address", "Start the base URL with `https://`."
    )


Origin = tuple[str, str | None, int | None]


PORTS: dict[str, int] = {"http": 80, "https": 443}


def origin_of(address: str) -> Origin:
    """The scheme, the host and the port an address is sent to. An address that
    states no port has its scheme's own.
    """

    parts = urlsplit(address)
    return (parts.scheme, parts.hostname, parts.port or PORTS.get(parts.scheme))


def held_to(hop: Any, placed: Sequence[PlacedCredential], home: Origin) -> Any:
    """Writes the placed credentials on a redirected request that stays at the
    origin its call was addressed to, and takes them off one that leaves it.

    The request is still sent, because a redirect to an address that needs no
    credential, such as a signed download link, has to keep working.
    """

    stays = origin_of(str(hop.url)) == home
    for entry in placed:
        credential = entry.credential
        if credential.location == "header":
            hop.headers.pop(credential.name, None)
            if stays:
                hop.headers[credential.name] = credential.value
        elif credential.location == "cookie":
            prefix = f"{credential.name}="
            sent: str = hop.headers.get("cookie", "")
            kept = [
                one.strip()
                for one in sent.split(";")
                if one.strip() and not one.strip().startswith(prefix)
            ]
            if stays:
                kept.append(f"{prefix}{credential.value}")
            hop.headers.pop("cookie", None)
            if kept:
                hop.headers["cookie"] = "; ".join(kept)
    return hop


def _as_placed(request: Any) -> Any:
    return request


def send_options(request: PreparedRequest) -> dict[str, Any]:
    return {"auth": _as_placed} if "authorization" in request.meta else {}


def send_once(
    client: HttpxLike, built: Any, request: PreparedRequest, stream: bool = False
) -> HttpxResponse:
    return client.send(built, stream=stream, **send_options(request))


def too_many_redirects(limit: int) -> TransportError:
    return TransportError(
        f"The API redirected the request more than {limit} times, so no reply was read."
    )


def send_at_origin(
    client: HttpxLike, built: Any, request: PreparedRequest, stream: bool = False
) -> HttpxResponse:
    """Sends a request, and follows each redirect itself where the call carries
    a credential, so that the credential goes to one origin only.

    A client that follows no redirect is sent through as it is.
    """

    placed = request.placed
    if not placed or not getattr(client, "follow_redirects", False):
        return send_once(client, built, request, stream)
    home = origin_of(str(built.url))
    limit: int = getattr(client, "max_redirects", 20)
    options = send_options(request)
    history: list[HttpxResponse] = []
    response = client.send(built, stream=stream, follow_redirects=False, **options)
    hop = getattr(response, "next_request", None)
    while hop is not None:
        response.close()
        if len(history) >= limit:
            raise too_many_redirects(limit)
        history.append(response)
        response = client.send(
            held_to(hop, placed, home), stream=stream, follow_redirects=False, **options
        )
        hop = getattr(response, "next_request", None)
    cast(Any, response).history = history
    return response


@dataclass
class HttpxTransport:
    client: HttpxLike | None = None
    factory: Callable[[], HttpxLike] | None = None
    name: str = "httpx2"
    _built: HttpxLike | None = field(default=None, init=False, repr=False)
    _lock: threading.Lock = field(
        default_factory=threading.Lock, init=False, repr=False
    )

    def __post_init__(self) -> None:
        if self.client is None and self.factory is None:
            raise ValueError("An httpx transport needs `client` or `factory`.")

    def _current(self) -> HttpxLike:
        if self.client is not None:
            return self.client
        if self._built is None:
            with self._lock:
                if self._built is None:
                    self._built = cast(Callable[[], HttpxLike], self.factory)()
        return self._built

    def close(self) -> None:
        built = self._built
        self._built = None
        if built is not None:
            built.close()

    def unary(self, request: PreparedRequest) -> RawResponse:
        if self.client is None:
            check_address(request.address)
        client = self._current()
        limit = _limit(request)
        deadline = None if limit is None else time.monotonic() + limit
        response = send_at_origin(
            client, build_httpx_request(client, request), request, deadline is not None
        )
        return response if deadline is None else _read_by(response, deadline, request)


class _EventLoop(Protocol):
    def is_closed(self) -> bool: ...


_Held = tuple[AsyncHttpxLike, AsyncGenerator[None, None]]


async def _closed_with_loop(client: AsyncHttpxLike) -> AsyncGenerator[None, None]:
    try:
        yield None
    finally:
        if not client.is_closed:
            await client.aclose()


def _held_by_loop(client: AsyncHttpxLike) -> AsyncGenerator[None, None]:
    held = _closed_with_loop(client)
    with contextlib.suppress(StopIteration):
        held.asend(None).send(None)
    return held


def async_send_once(
    client: AsyncHttpxLike, built: Any, request: PreparedRequest, stream: bool = False
) -> Awaitable[AsyncHttpxResponse]:
    return client.send(built, stream=stream, **send_options(request))


async def async_send_at_origin(
    client: AsyncHttpxLike, built: Any, request: PreparedRequest, stream: bool = False
) -> AsyncHttpxResponse:
    """`send_at_origin`, for the async client."""

    placed = request.placed
    if not placed or not getattr(client, "follow_redirects", False):
        return await async_send_once(client, built, request, stream)
    home = origin_of(str(built.url))
    limit: int = getattr(client, "max_redirects", 20)
    options = send_options(request)
    history: list[Any] = []
    send: Any = client.send
    response = await send(built, stream=stream, follow_redirects=False, **options)
    hop = getattr(response, "next_request", None)
    while hop is not None:
        await response.aclose()
        if len(history) >= limit:
            raise too_many_redirects(limit)
        history.append(response)
        response = await send(
            held_to(hop, placed, home), stream=stream, follow_redirects=False, **options
        )
        hop = getattr(response, "next_request", None)
    response.history = history
    reply: AsyncHttpxResponse = response
    return reply


@dataclass
class AsyncHttpxTransport:
    client: AsyncHttpxLike | None = None
    factory: Callable[[], AsyncHttpxLike] | None = None
    name: str = "httpx2"
    _clients: dict[_EventLoop, _Held] = field(
        default_factory=lambda: {}, init=False, repr=False
    )
    _lock: threading.Lock = field(
        default_factory=threading.Lock, init=False, repr=False
    )

    def __post_init__(self) -> None:
        if self.client is None and self.factory is None:
            raise ValueError("An async httpx transport needs `client` or `factory`.")

    def _current(self) -> AsyncHttpxLike:
        if self.client is not None:
            return self.client
        import asyncio

        loop = asyncio.get_running_loop()
        built = self._clients.get(loop)
        if built is not None:
            return built[0]
        with self._lock:
            for closed in [loop_ for loop_ in self._clients if loop_.is_closed()]:
                del self._clients[closed]
            if loop not in self._clients:
                client = cast(Callable[[], AsyncHttpxLike], self.factory)()
                self._clients[loop] = (client, _held_by_loop(client))
            return self._clients[loop][0]

    async def unary(self, request: PreparedRequest) -> RawResponse:
        import asyncio

        if self.client is None:
            check_address(request.address)
        client = self._current()
        sending = async_send_at_origin(
            client, build_httpx_request(client, request), request
        )
        limit = _limit(request)
        if limit is None:
            return await sending
        try:
            return await asyncio.wait_for(sending, limit)
        except asyncio.TimeoutError as cause:
            raise timeout_error(request) from cause

    async def aclose(self) -> None:
        with self._lock:
            built = list(self._clients.items())
            self._clients.clear()
        for loop, (client, _) in built:
            if not client.is_closed and not loop.is_closed():
                await client.aclose()


def create_httpx_transport(
    client: HttpxLike | None = None,
    name: str = "httpx2",
    *,
    factory: Callable[[], HttpxLike] | None = None,
) -> HttpxTransport:
    return HttpxTransport(client=client, factory=factory, name=name)


def create_async_httpx_transport(
    client: AsyncHttpxLike | None = None,
    name: str = "httpx2",
    *,
    factory: Callable[[], AsyncHttpxLike] | None = None,
) -> AsyncHttpxTransport:
    return AsyncHttpxTransport(client=client, factory=factory, name=name)
