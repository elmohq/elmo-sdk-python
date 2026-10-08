from __future__ import annotations

import json
import re
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeGuard, cast

from typing_extensions import TypeVar

from .backoff import retry_after_delay
from .text import to_text
from .types import Interaction, PreparedRequest, RawResponse

if TYPE_CHECKING:
    from ...types.shared.error import Error


def _restored(kind: Any, args: Any, state: dict[str, Any]) -> Any:
    error = kind.__new__(kind)
    error.args = args
    error.__dict__.update(state)
    return error


class ElmoError(Exception):
    """The base of every error this SDK raises, including one from a call that never
    arrived.
    """

    def __reduce__(self) -> Any:
        return (_restored, (type(self), self.args, dict(self.__dict__)))


REQUEST_ID_FALLBACKS: list[str] = ["x-correlation-id", "cf-ray"]


REQUEST_ID_NAME = re.compile(r"(?:^|-)request-?id$")


def request_id_of(response: Any) -> str | None:
    meta: Mapping[str, str] = getattr(response, "headers", None) or {}
    for name, named in meta.items():
        if named and REQUEST_ID_NAME.search(name.lower()):
            return named
    for header in REQUEST_ID_FALLBACKS:
        value: str | None = meta.get(header)
        if value:
            return value
    return None


class DecodeError(ElmoError):
    """A reply from the API that this SDK could not read, whatever its status."""

    def __init__(
        self,
        message: str,
        at: str | None = None,
        response: RawResponse | None = None,
        value: Any = None,
    ) -> None:
        request_id = request_id_of(response)
        super().__init__(
            f'{message} The request id is "{request_id}".' if request_id else message
        )
        self.at: str | None = at
        """Where the value sat, or `None` where the whole reply failed."""
        self.request_id: str | None = request_id
        """The request id to quote when reporting this failure."""
        self.response = response
        """The reply. Its body is already read."""
        self.status: int | None = getattr(response, "status_code", None)
        """The reply's status. `None` where there is no `response`."""
        self.value: Any = value
        """What the API sent. The message holds only a short form of it."""


_USERINFO_RE = re.compile(r"^([a-z][a-z\d+.-]*://)[^/?#@]*@", re.IGNORECASE | re.ASCII)


def safe_address(url: Any) -> str:
    return _USERINFO_RE.sub(r"\1", str(url).split("?")[0])


FailureBody = Mapping[str, Any] | list[Any]
"""A decoded failure body: a JSON object or a JSON array."""


TBody_co = TypeVar("TBody_co", covariant=True, default="Error")


CODE_KEYS: list[str] = ["code", "error_code", "errorCode", "error_type", "errorType"]


def _is_mapping(value: Any) -> TypeGuard[Mapping[str, Any]]:
    return isinstance(value, Mapping)


def _stated(bag: Mapping[str, Any], keys: list[str]) -> str | int | None:
    for key in keys:
        value = bag.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if key in CODE_KEYS and isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def describe_code(body: Any) -> str | int | None:
    if not _is_mapping(body):
        return None
    direct = _stated(body, CODE_KEYS)
    if direct is not None:
        return direct
    for value in body.values():
        if _is_mapping(value):
            nested = _stated(value, CODE_KEYS)
            if nested is not None:
                return nested
    return None


MESSAGE_KEYS: list[str] = [
    "message",
    "error_message",
    "errorMessage",
    "error",
    "detail",
    "title",
    "description",
]


MAX_MESSAGE_BODY = 200


def _shorten(text: str) -> str:
    line = " ".join(text.split())
    if len(line) <= MAX_MESSAGE_BODY:
        return line
    cut = line[:MAX_MESSAGE_BODY]
    space = cut.rfind(" ")
    kept = cut[:space] if space > MAX_MESSAGE_BODY // 2 else cut
    return f"{kept.rstrip()}…"


def describe_stated_failure(body: Any) -> str | None:
    if isinstance(body, str):
        return _shorten(body.strip()) or None
    if _is_mapping(body):
        direct = _stated(body, MESSAGE_KEYS)
        if direct:
            return _shorten(str(direct))
        values: Iterable[Any] = body.values()
    elif isinstance(body, list):
        values = cast(Iterable[Any], body)
    else:
        return None
    for value in values:
        if _is_mapping(value):
            nested = _stated(value, MESSAGE_KEYS)
            if nested:
                return _shorten(str(nested))
    try:
        encoded = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return None
    return _shorten(encoded) if encoded not in ("{}", "[]") else None


def read_error(body: Any) -> Error:
    from ...types.shared.error import Error

    return Error.model_validate(body)


BodyReaders = Mapping[str, Sequence[Callable[[Any], Any]]]


BODY_READERS: BodyReaders = {
    "400": (read_error,),
    "401": (read_error,),
    "402": (read_error,),
    "403": (read_error,),
    "404": (read_error,),
    "409": (read_error,),
    "429": (read_error,),
    "500": (read_error,),
}


def range_key(status: int) -> str:
    return "5XX" if status > 599 else f"{status // 100}XX"


def readers_for(table: BodyReaders, status: int) -> Sequence[Callable[[Any], Any]]:
    for key in (str(status), range_key(status), "default"):
        if key in table:
            return table[key]
    return ()


def read_data(status: int, body: Any) -> Any:
    if not isinstance(body, (Mapping, list)):
        return None
    for read in readers_for(BODY_READERS, status):
        try:
            return read(body)
        except Exception:
            continue
    return None


class APIError(ElmoError, Generic[TBody_co]):
    """A failure the API answered with, so there is a status and a reply to read."""

    def __init__(
        self,
        status: int,
        body: Any = None,
        response: RawResponse | None = None,
        note: str | None = None,
    ) -> None:
        reason = getattr(response, "reason_phrase", "") or ""
        stated = f"{status} {reason}" if reason else f"{status}"
        url = getattr(response, "url", "") or ""
        request_id = request_id_of(response)
        where = f' for "{safe_address(url)}"' if url else ""
        if request_id:
            where += f' (request id "{request_id}")'
        said = describe_stated_failure(body)
        structured = isinstance(body, (Mapping, list))
        if note:
            tail = f". {note}" + (f" The API said: {said}" if said else "")
        else:
            tail = f": {said}" if said else "."
        super().__init__(f"The API answered {stated}{where}{tail}")

        self.body: FailureBody | None = body if structured else None
        """The decoded failure body. `None` where the reply carried none, or carried
        text such as a proxy's page, which is in `text`.
        """
        self.code: str | int | None = describe_code(body)
        """The API's own error code, read from the failure body. `None` where it carried
        none.
        """
        self.data: TBody_co | None = read_data(status, body)
        """The failure body, read as the model the API description gives its status.
        `None` where it gives none, or where the body does not match, which `body`
        still holds.

        """
        self.headers: dict[str, str] = dict(getattr(response, "headers", None) or {})
        self.request_id: str | None = request_id
        """The request id to quote when reporting this failure."""
        self.response = response
        """The reply that carried this failure. Its body is already read."""
        self.retry_after_seconds: float | None = retry_after_delay(
            response, now=time.time()
        )
        """Seconds the API asked to wait before trying again."""
        self.status = status
        self.text: str | None = body if isinstance(body, str) else None
        """The failure body where the API sent text rather than JSON, such as a
        proxy's page. The message holds only its start.
        """


def empty_path_parameter(name: str, url: str) -> ElmoError:
    return ElmoError(
        f"Path parameter `{name}` is empty. `{url}` cannot be sent without it."
    )


TRANSPORT_MESSAGES: dict[str, str] = {
    "connect": "The request never reached the API.",
    "other": "The connection failed before the whole reply arrived.",
    "timeout": "The API did not answer in time.",
}


@dataclass(frozen=True)
class TransportFailure:
    stage: str
    reached_server: str
    aborted: bool = False
    cause: BaseException | None = None


class TransportError(ElmoError, ConnectionError):
    """Raised when no whole answer arrived, so there is no reply to go on. Also a
    builtin `ConnectionError`, so retry code that knows no SDK catches it.
    """

    def __init__(
        self, message: str, kind: str = "other", failure: TransportFailure | None = None
    ) -> None:
        super().__init__(message)
        self.kind: str = kind
        """Which way it failed: `"connect"`, `"timeout"`, or `"other"`."""
        unreached = kind == "connect"
        self.reached_server: str = (
            failure.reached_server if failure else "no" if unreached else "maybe"
        )
        """Whether the API can have acted on the request: `"no"`, `"maybe"`, or
        `"yes"`. After `"no"`, the call is safe to send again, whatever its method.
        """
        self.stage: str = (
            failure.stage if failure else "connect" if unreached else "receive"
        )
        """How far the request got: `"resolve"`, `"connect"`, `"tls"`, `"send"`, or
        `"receive"`.
        """


class TransportTimeoutError(TransportError, TimeoutError):
    """Raised when a call waited on the API for as long as it allowed, from
    sending the request to the last byte of the reply.

    A reply with status 408 is not one of these.
    """

    def __init__(self, timeout: float | None = None, target: str | None = None) -> None:
        message = TRANSPORT_MESSAGES["timeout"]
        if timeout is not None:
            message = f"{target or 'The request'} timed out after {timeout:g} s waiting on the API. Pass a larger `timeout` with the call, or `timeout=False` to wait as long as it takes."
        super().__init__(message, kind="timeout")
        self.timeout_seconds: float | None = timeout
        """Seconds the call was allowed to wait on the API."""


def _target(request: PreparedRequest) -> str:
    method = (request.operation.method or "").upper()
    address = f'"{safe_address(request.address)}"'
    return f"{method} {address}" if method else address


def timeout_error(request: PreparedRequest | None) -> TransportTimeoutError:
    limit = request.options.get("timeout") if request is not None else None
    if request is None or isinstance(limit, bool):
        return TransportTimeoutError()
    if not isinstance(limit, (int, float)) or limit <= 0:
        return TransportTimeoutError()
    return TransportTimeoutError(float(limit), _target(request))


def unsendable_address(address: str, problem: str, fix: str) -> ElmoError:
    return ElmoError(f'"{address}" {problem}, so the request was not sent. {fix}')


class MissingCredentialError(ElmoError):
    """Raised before the request goes out, when no credential satisfied the call."""

    def __init__(self, message: str, schemes: list[str] | None = None) -> None:
        super().__init__(message)
        self.schemes: list[str] = list(schemes or [])
        """Credential options that would have satisfied the call."""


def unsendable(held: str) -> str:
    return f"{held} holds a line break or another character a header cannot carry, so the request was not sent."


def unsendable_timeout(limit: Any) -> ElmoError:
    return ElmoError(
        f"`timeout` is {limit!r}, which is not a time limit, so the request was not sent. Pass a number of seconds, or `False` for none.",
    )


class UnsupportedInteractionError(ElmoError):
    def __init__(
        self, transport: str, interaction: Interaction, method: str | None = None
    ) -> None:
        super().__init__(
            f'Transport "{transport}" cannot send this call. It has no "{method or interaction}" method.',
        )
        self.interaction = interaction
        self.transport = transport


BROKEN: dict[str, str] = {
    "BrokenPipeError": "send",
    "ConnectionAbortedError": "receive",
    "ConnectionResetError": "receive",
    "HTTPError": "receive",
    "RequestError": "receive",
    "TransportError": "receive",
    "WriteError": "send",
    "WriteTimeout": "send",
}


UNREACHED: dict[str, str] = {
    "ConnectError": "connect",
    "ConnectTimeout": "connect",
    "ConnectionError": "connect",
    "PoolTimeout": "connect",
}


def failure_of(error: BaseException) -> TransportFailure | None:
    stage = getattr(error, "stage", None)
    reached = getattr(error, "reached_server", None)
    if isinstance(stage, str) and isinstance(reached, str):
        return TransportFailure(
            stage, reached, getattr(error, "aborted", False) is True, error.__cause__
        )
    names = [base.__name__ for base in type(error).__mro__]
    for name in names:
        if name in BROKEN:
            return TransportFailure(BROKEN[name], "maybe", cause=error)
        if name in UNREACHED:
            return TransportFailure(UNREACHED[name], "no", cause=error)
    return None


def to_transport_error(
    error: BaseException, request: PreparedRequest | None = None
) -> BaseException:
    if isinstance(error, ElmoError):
        return error
    names = {base.__name__ for base in type(error).__mro__}
    if "LocalProtocolError" in names:
        return ElmoError(
            "The HTTP client refused to write the request, so it was not sent."
        )
    failure = failure_of(error)
    if failure is not None and failure.reached_server == "no":
        return TransportError(TRANSPORT_MESSAGES["connect"], "connect", failure)
    if "TimeoutException" in names or "Timeout" in names:
        return timeout_error(request)
    if failure is not None:
        return TransportError(TRANSPORT_MESSAGES["other"], "other", failure)
    return error


def unsendable_header(name: str) -> ElmoError:
    return ElmoError(unsendable(f"Header `{name}`"))


def unreadable_value(
    at: str | None,
    value: Any = None,
    response: RawResponse | None = None,
    missing: bool = False,
) -> DecodeError:
    if missing:
        said = "nothing"
    elif isinstance(value, str):
        said = f'"{_shorten(value)}"'
    else:
        said = _shorten(to_text(value))
    where = "the reply" if at is None else f"`{at}` from the reply"
    return DecodeError(
        f"Could not read {where}: the API sent {said}.",
        at=at,
        response=response,
        value=value,
    )


def unsendable_input(name: str, problems: Sequence[Mapping[str, Any]]) -> ElmoError:
    first: Mapping[str, Any] = problems[0] if problems else {}
    path = ".".join([name, *(str(part) for part in first.get("loc", ()))])
    more = len(problems) - 1
    rest = (
        f" It breaks {more} more {'rule' if more == 1 else 'rules'}."
        if more > 0
        else ""
    )
    return ElmoError(
        f"`{path}` is not valid, so the request was not sent: {first.get('msg', 'it breaks a rule')}.{rest}",
    )
