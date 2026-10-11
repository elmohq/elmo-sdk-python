from __future__ import annotations

import functools
from collections.abc import Awaitable, Callable, Mapping
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Generic, cast

from typing_extensions import ParamSpec, TypeVar

from .errors import (
    ElmoError,
    range_key,
    sniff_request_id,
    undeclared_body,
    unreadable_value,
)
from .types import OperationDescriptor

T = TypeVar("T")


Readers = Mapping[str, Callable[[Any], T] | None]


Read = Callable[[Any], T] | Readers[T]


@dataclass
class Response(Generic[T]):
    """A call's answer, and the reply that carried it."""

    data: T
    """What the call would have handed back on its own."""
    request_id: str | None
    """The request id to quote when reporting a problem with this call."""
    response: Any
    """The transport's own reply."""
    status: int


_wants_response: ContextVar[bool] = ContextVar("hey_api_wants_response", default=False)


CONTAINERS = ("dict_type", "list_type", "model_type")


def read_reply(
    read: Callable[[Any], T], payload: Any, response: Any = None, whole: bool = False
) -> T:
    try:
        return read(payload)
    except ElmoError:
        raise
    except Exception as error:
        owner = getattr(read, "__self__", None)
        at: str | None = getattr(error, "title", None) or getattr(
            owner, "__name__", None
        )
        listed = getattr(error, "errors", None)
        issues = cast(list[Any], listed()) if callable(listed) else []
        if not issues:
            raise unreadable_value(at, payload, response) from error
        first = issues[0]
        if whole and not first.get("loc") and first.get("type") in CONTAINERS:
            raise undeclared_body(response, payload) from error
        for part in first.get("loc", ()):
            if isinstance(part, int):
                at = f"{at or ''}[{part}]"
            else:
                at = f"{at}.{part}" if at else str(part)
        missing = first.get("type") == "missing"
        value = None if missing else first.get("input")
        raise unreadable_value(at, value, response, missing) from error


def _nothing(payload: Any) -> None:
    return None


def as_it_arrived(payload: Any) -> Any:
    return payload


def reader_for(read: Read[T], response: Any) -> Callable[[Any], T]:
    given: Any = read
    if not isinstance(given, Mapping):
        return cast("Callable[[Any], T]", given)
    readers = cast("Readers[T]", given)
    stated: dict[str, Callable[[Any], T] | None] = {}
    for key, reader in readers.items():
        stated[key.upper()] = reader
    status = getattr(response, "status_code", None)
    keys = (
        ["DEFAULT"] if status is None else [str(status), range_key(status), "DEFAULT"]
    )
    for key in keys:
        if key in stated:
            found = stated[key]
            return cast("Callable[[Any], T]", _nothing if found is None else found)
    return cast("Callable[[Any], T]", as_it_arrived)


def _answer(read: Read[T], exchange: Any) -> T:
    response = exchange.response
    data = read_reply(reader_for(read, response), exchange.data, response, True)
    if not _wants_response.get():
        return data
    status: int = getattr(response, "status_code", 0)
    return cast(
        "T",
        Response(
            data=data,
            request_id=sniff_request_id(response),
            response=response,
            status=status,
        ),
    )


def send(
    client: Any,
    operation: OperationDescriptor,
    options: dict[str, Any] | None = None,
    read: Read[T] = as_it_arrived,
) -> T:
    exchange = client.exchange(operation, options)
    return _answer(read, exchange)


P = ParamSpec("P")


R = TypeVar("R")


def with_response(method: Callable[P, R]) -> Callable[P, Response[R]]:
    @functools.wraps(method)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> Response[R]:
        token = _wants_response.set(True)
        try:
            return cast("Response[R]", method(*args, **kwargs))
        finally:
            _wants_response.reset(token)

    return wrapped


async def async_send(
    client: Any,
    operation: OperationDescriptor,
    options: dict[str, Any] | None = None,
    read: Read[T] = as_it_arrived,
) -> T:
    exchange = await client.exchange(operation, options)
    return _answer(read, exchange)


def async_with_response(
    method: Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[Response[R]]]:
    @functools.wraps(method)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> Response[R]:
        token = _wants_response.set(True)
        try:
            return cast("Response[R]", await method(*args, **kwargs))
        finally:
            _wants_response.reset(token)

    return wrapped
