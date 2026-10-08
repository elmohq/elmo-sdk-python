from __future__ import annotations

from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, TypeVar

import httpx2
import pytest

from elmo_sdk import AsyncElmo

if TYPE_CHECKING:
    from elmo_sdk import Elmo

SUCCESS: dict[str, Any] = {
    "body": {
        "keyType": "admin",
        "organizationId": "test",
        "organizationName": "test",
        "scopes": ["read"],
        "brandIds": ["test"],
        "createdAt": "2026-01-01T00:00:00Z",
        "expiresAt": "2026-01-01T00:00:00Z",
        "rateLimit": {"limit": 0, "window": "minute"},
        "createdBy": "test",
        "lastUsedAt": "2026-01-01T00:00:00Z",
    },
    "status": 200,
}


class StandIn:
    """A stand-in for the API, passed to the client as its `http_client`. It
    answers each request with the next of `replies`, then the last one again,
    and keeps every request it is sent. A reply that is `cut` fails as the
    HTTP library does when the connection is lost, or when nothing more comes.
    """

    def __init__(self, *replies: dict[str, Any]) -> None:
        self.replies = replies
        self.requests: list[httpx2.Request] = []
        self.http_client = httpx2.Client(transport=httpx2.MockTransport(self.answer))

    def answer(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        reply = self.replies[min(len(self.requests), len(self.replies)) - 1]
        cut = reply.get("cut")
        if cut == "broken":
            raise httpx2.ReadError("The connection was lost.", request=request)
        if cut == "stalled":
            raise httpx2.ReadTimeout("The API did not answer in time.", request=request)
        if "body" in reply:
            return httpx2.Response(
                reply["status"], headers=reply.get("headers"), json=reply["body"]
            )
        return httpx2.Response(reply["status"], headers=reply.get("headers"))


def unanswered(request: httpx2.Request) -> httpx2.Response:
    """Answers no request in time, as a transport handler."""

    raise httpx2.ReadTimeout("The API did not answer in time.", request=request)


class Clients:
    """Builds the class a test was given, plain or awaited, over a mock transport."""

    def __init__(self, root: type[Elmo | AsyncElmo]) -> None:
        self.root = root

    def __call__(
        self,
        handler: Callable[[httpx2.Request], httpx2.Response] | None = None,
        **options: Any,
    ) -> Elmo | AsyncElmo:
        """Builds the class with `options`, answering with `handler` where given."""

        if handler is not None:
            options["http_client"] = self.http_client(handler)
        return self.root(**options)

    def http_client(
        self, handler: Callable[[httpx2.Request], httpx2.Response]
    ) -> httpx2.Client | httpx2.AsyncClient:
        """A client of the library the class sends with, answering with `handler`."""

        transport = httpx2.MockTransport(handler)
        if self.root is AsyncElmo:
            return httpx2.AsyncClient(transport=transport)
        return httpx2.Client(transport=transport)

    def own_transport(
        self,
        monkeypatch: pytest.MonkeyPatch,
        handler: Callable[[httpx2.Request], httpx2.Response],
    ) -> list[object]:
        """Answers each call with `handler` through the transport the class opens for
        itself, and returns the list of each one it closes.
        """

        closed: list[object] = []
        if self.root is AsyncElmo:

            async def handle_async_request(
                _transport: httpx2.AsyncHTTPTransport, request: httpx2.Request
            ) -> httpx2.Response:
                return handler(request)

            async def aclose(transport: httpx2.AsyncHTTPTransport) -> None:
                closed.append(transport)

            monkeypatch.setattr(
                httpx2.AsyncHTTPTransport, "handle_async_request", handle_async_request
            )
            monkeypatch.setattr(httpx2.AsyncHTTPTransport, "aclose", aclose)
            return closed

        def handle_request(
            _transport: httpx2.HTTPTransport, request: httpx2.Request
        ) -> httpx2.Response:
            return handler(request)

        def close(transport: httpx2.HTTPTransport) -> None:
            closed.append(transport)

        monkeypatch.setattr(httpx2.HTTPTransport, "handle_request", handle_request)
        monkeypatch.setattr(httpx2.HTTPTransport, "close", close)
        return closed


T = TypeVar("T")


async def result(value: T | Awaitable[T]) -> T:
    """What a call returns, awaited where the class awaits its calls."""

    if isinstance(value, Awaitable):
        return await value
    return value


@asynccontextmanager
async def opened(client: Elmo | AsyncElmo) -> AsyncGenerator[Elmo | AsyncElmo, None]:
    """Opens the client as a caller does, and closes it on the way out."""

    if isinstance(client, AsyncElmo):
        async with client:
            yield client
    else:
        with client:
            yield client
