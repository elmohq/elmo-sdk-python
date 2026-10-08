from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Sequence
from typing import TypedDict, cast

from typing_extensions import TypeVar

from ..core.errors import ElmoError
from ..core.features import Feature
from ..core.types import FeatureContext, PreparedRequest, Result

TValue = TypeVar("TValue")


async def _awaited(value: TValue | Awaitable[TValue]) -> TValue:
    if inspect.isawaitable(value):
        return await value
    return value


ErrorHook = Callable[
    [BaseException, PreparedRequest], BaseException | Awaitable[BaseException]
]
"""A hook that runs when a call fails, and returns the error to raise."""


RequestHook = Callable[[PreparedRequest], None | Awaitable[None]]
"""A hook that runs on the built request, last before it is sent."""


ResponseHook = Callable[[Result, PreparedRequest], Result | Awaitable[Result]]
"""A hook that runs on the reply, and returns the result to read."""


class Interceptors(TypedDict, total=False):
    """Hooks of your own, run in order at three points in every call."""

    error: Sequence[ErrorHook]
    """Runs when a call fails. Return the error to raise, which may be another."""
    request: Sequence[RequestHook]
    """Runs on the built request, last before it is sent."""
    response: Sequence[ResponseHook]
    """Runs on the reply. Return the result to read, which may be another."""


def _declared(request: PreparedRequest) -> Interceptors:
    declared = request.options.get("interceptors")
    if not isinstance(declared, dict):
        return Interceptors()
    return cast(Interceptors, declared)


def _settled(value: TValue | Awaitable[TValue], phase: str) -> TValue:
    if inspect.isawaitable(value):
        if inspect.iscoroutine(value):
            value.close()
        raise ElmoError(
            f"The {phase} interceptor returned an awaitable. Only the async client waits for one.",
        )
    return value


class InterceptorsFeature(Feature):
    name = "interceptors"

    def on_request(self, request: PreparedRequest, ctx: FeatureContext) -> None:
        for hook in _declared(request).get("request", ()):
            _settled(hook(request), "request")

    async def on_async_request(
        self, request: PreparedRequest, ctx: FeatureContext
    ) -> None:
        for hook in _declared(request).get("request", ()):
            await _awaited(hook(request))

    def on_result(
        self, result: Result, request: PreparedRequest, ctx: FeatureContext
    ) -> Result:
        for hook in _declared(request).get("response", ()):
            result = _settled(hook(result, request), "response")
        return result

    async def on_async_result(
        self, result: Result, request: PreparedRequest, ctx: FeatureContext
    ) -> Result:
        for hook in _declared(request).get("response", ()):
            result = await _awaited(hook(result, request))
        return result

    def on_error(
        self, error: BaseException, request: PreparedRequest, ctx: FeatureContext
    ) -> BaseException:
        for hook in _declared(request).get("error", ()):
            error = _settled(hook(error, request), "error")
        return error

    async def on_async_error(
        self, error: BaseException, request: PreparedRequest, ctx: FeatureContext
    ) -> BaseException:
        for hook in _declared(request).get("error", ()):
            error = await _awaited(hook(error, request))
        return error
