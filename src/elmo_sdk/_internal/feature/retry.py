from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from typing import Any, cast

from ..core.backoff import (
    BACKOFF_DELAY,
    BACKOFF_MAX_DELAY,
    MAX_RETRY_AFTER,
    TIMER_LIMIT,
    Jitter,
    RetryAfterHeader,
    backoff_delay,
    exceeds_max_retry_after,
    retry_after_delay,
)
from ..core.errors import DecodeError, TransportError
from ..core.features import Feature
from ..core.types import (
    AsyncSend,
    FeatureContext,
    PreparedRequest,
    Result,
    RetryOptions,
    RetryRules,
    Send,
)

DEFAULT_MAX_RETRIES: int = 2


@dataclass(frozen=True)
class _Rules:
    budget: float | None
    delay: float
    jitter: Jitter
    max_delay: float
    max_retries: int
    max_retry_after: float
    methods: Sequence[str] | None
    retry_after: Sequence[RetryAfterHeader] | None
    retry_on_timeout: bool
    statuses: Sequence[int] | None
    strategy: str
    retry_delay: Callable[[Result, PreparedRequest, int], float | None] | None = None
    retry_on: Callable[[Result, PreparedRequest], bool] | None = None


def _asked_for(rules: _Rules, result: Result) -> float | None:
    if result.response is None:
        return None
    headers = None if rules.retry_after is None else list(rules.retry_after)
    return retry_after_delay(result.response, headers, now=time.time())


def _backoff(rules: _Rules, attempt: int) -> float:
    return backoff_delay(
        attempt, rules.delay, rules.max_delay, rules.jitter, rules.strategy
    )


PERMANENT_STATUSES: list[int] = [501, 505, 506, 508, 510, 511]


REFUSED_STATUSES: list[int] = [408, 425, 429]


RETRY_HEADER = "x-should-retry"


def _worth_repeating(
    rules: _Rules, result: Result, request: PreparedRequest, repeatable: bool
) -> bool:
    response = result.response
    if response is None:
        return False
    status = response.status_code
    asked = response.headers.get(RETRY_HEADER)
    invited = asked == "true" and status >= 400
    if not repeatable and not invited and status not in REFUSED_STATUSES:
        return False
    if rules.retry_on is not None:
        return rules.retry_on(result, request)
    if asked == "false":
        return False
    if invited:
        return True
    if rules.statuses is not None:
        return status in rules.statuses
    if status >= 500:
        return status not in PERMANENT_STATUSES
    return status in REFUSED_STATUSES


def _delay_after(
    rules: _Rules,
    result: Result,
    request: PreparedRequest,
    repeatable: bool,
    attempt: int,
    last: bool,
) -> float | None:
    if last or not _worth_repeating(rules, result, request, repeatable):
        return None
    if rules.retry_delay is not None:
        chosen = rules.retry_delay(result, request, attempt)
        if chosen is not None:
            return chosen
    asked = _asked_for(rules, result)
    if exceeds_max_retry_after(asked, rules.max_retry_after):
        return None
    if asked is not None:
        return asked
    return _backoff(rules, attempt)


def _worth_repeating_error(
    rules: _Rules, error: BaseException, request: PreparedRequest, repeatable: bool
) -> bool:
    if not isinstance(error, TransportError):
        return False
    if error.reached_server != "no" and not repeatable:
        return False
    if rules.retry_on is not None:
        return rules.retry_on(Result(error=error), request)
    return error.kind != "timeout" or rules.retry_on_timeout


def _delay_after_error(
    rules: _Rules,
    error: BaseException,
    request: PreparedRequest,
    repeatable: bool,
    attempt: int,
    last: bool,
) -> float | None:
    if isinstance(error, DecodeError) and error.response is not None:
        result = Result(response=error.response)
        return _delay_after(rules, result, request, repeatable, attempt, last)
    if last or not _worth_repeating_error(rules, error, request, repeatable):
        return None
    if rules.retry_delay is not None:
        chosen = rules.retry_delay(Result(error=error), request, attempt)
        if chosen is not None:
            return chosen
    return _backoff(rules, attempt)


def _log_retry(
    request: PreparedRequest, wait: float, attempt: int, retries: int, after: Result
) -> None:
    log = getattr(request, "log", None)
    if log is not None:
        log.retrying(wait, attempt + 1, retries, after)


def _merged(rules: _Rules, stated: RetryRules) -> _Rules:
    fields = _Rules.__dataclass_fields__
    changes: dict[str, Any] = {}
    for name, value in stated.items():
        if name in fields:
            changes[name] = value
    headers = changes.get("retry_after")
    if isinstance(headers, bool):
        changes["retry_after"] = None if headers else []
    return replace(rules, **changes)


IDEMPOTENT_METHODS: list[str] = ["delete", "get", "head", "options", "put", "trace"]


def _repeatable(rules: _Rules, request: PreparedRequest) -> bool:
    method = (request.operation.method or "").lower()
    if not method:
        return False
    allowed = IDEMPOTENT_METHODS
    if rules.methods is not None:
        allowed = [name.lower() for name in rules.methods]
    if method in allowed:
        return True
    key = request.operation.idempotency
    return key is not None and request.meta.get(key) is not None


def _retries(stated: _Rules, own: RetryOptions | None, request: PreparedRequest) -> int:
    if own is not None and "max_retries" in own:
        return max(0, own["max_retries"])
    retries = request.options.get("max_retries")
    if isinstance(retries, int) and not isinstance(retries, bool):
        return max(0, retries)
    return stated.max_retries


def _spent(rules: _Rules, started: float, wait: float) -> bool:
    budget = rules.budget
    return budget is not None and time.monotonic() - started + wait >= budget


class RetryFeature(Feature):
    name = "retry"

    def __init__(
        self,
        budget: float | None = None,
        delay: float = BACKOFF_DELAY,
        jitter: Jitter = True,
        max_delay: float = BACKOFF_MAX_DELAY,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_retry_after: float = MAX_RETRY_AFTER,
        methods: list[str] | None = None,
        retry_after: list[RetryAfterHeader] | None = None,
        retry_delay: Callable[[Result, PreparedRequest, int], float | None]
        | None = None,
        retry_on: Callable[[Result, PreparedRequest], bool] | None = None,
        retry_on_timeout: bool = False,
        statuses: list[int] | None = None,
        strategy: str = "exponential",
    ) -> None:
        self.rules = _Rules(
            budget=budget,
            delay=delay,
            jitter=jitter,
            max_delay=max_delay,
            max_retries=max_retries,
            max_retry_after=max_retry_after,
            methods=methods,
            retry_after=retry_after,
            retry_on_timeout=retry_on_timeout,
            statuses=statuses,
            strategy=strategy,
            retry_delay=retry_delay,
            retry_on=retry_on,
        )
        self.declared: dict[int, tuple[RetryRules, _Rules]] = {}

    def on_send(
        self, request: PreparedRequest, send: Send, ctx: FeatureContext
    ) -> Result:
        rules = self._resolve(request)
        if rules is None:
            return send(request)
        repeatable = _repeatable(rules, request)
        started = time.monotonic()
        attempt = 0

        while True:
            last = attempt >= rules.max_retries
            request.attempt = attempt
            try:
                result = send(request)
                wait = _delay_after(rules, result, request, repeatable, attempt, last)
                if wait is None or _spent(rules, started, wait):
                    return result
            except Exception as error:
                wait = _delay_after_error(
                    rules, error, request, repeatable, attempt, last
                )
                if wait is None or _spent(rules, started, wait):
                    raise
                result = Result(error=error)
            _log_retry(request, wait, attempt, rules.max_retries, result)
            time.sleep(min(wait, TIMER_LIMIT))
            attempt += 1

    async def on_async_send(
        self, request: PreparedRequest, send: AsyncSend, ctx: FeatureContext
    ) -> Result:
        rules = self._resolve(request)
        if rules is None:
            return await send(request)
        repeatable = _repeatable(rules, request)
        started = time.monotonic()
        attempt = 0

        while True:
            last = attempt >= rules.max_retries
            request.attempt = attempt
            try:
                result = await send(request)
                wait = _delay_after(rules, result, request, repeatable, attempt, last)
                if wait is None or _spent(rules, started, wait):
                    return result
            except Exception as error:
                wait = _delay_after_error(
                    rules, error, request, repeatable, attempt, last
                )
                if wait is None or _spent(rules, started, wait):
                    raise
                result = Result(error=error)
            _log_retry(request, wait, attempt, rules.max_retries, result)
            import asyncio

            await asyncio.sleep(wait)
            attempt += 1

    on_open = on_send
    on_async_open = on_async_send

    def _declared(self, declared: RetryRules) -> _Rules:
        held = self.declared.get(id(declared))
        if held is None or held[0] is not declared:
            held = (declared, _merged(self.rules, declared))
            self.declared[id(declared)] = held
        return held[1]

    def _resolve(self, request: PreparedRequest) -> _Rules | None:
        called = request.options.get("retry")
        if called is False:
            return None
        declared = request.operation.retry
        if declared is False and called is None:
            return None
        stated = self._declared(declared) if declared else self.rules
        own = cast(RetryOptions, called) if isinstance(called, dict) else None
        rules = stated if own is None else _merged(stated, own)
        retries = _retries(stated, own, request)
        if retries < 1:
            return None
        return (
            rules
            if retries == rules.max_retries
            else replace(rules, max_retries=retries)
        )
