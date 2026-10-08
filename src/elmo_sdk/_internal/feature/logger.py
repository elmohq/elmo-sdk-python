from __future__ import annotations

import itertools
import logging
import re
import time
from collections.abc import Mapping
from typing import Any, Literal

from ..core.errors import safe_address
from ..core.features import Feature
from ..core.types import (
    AsyncSend,
    AuthScheme,
    FeatureContext,
    OperationDescriptor,
    PreparedRequest,
    Result,
    Send,
)

LEVELS: dict[str, int] = {
    "debug": logging.DEBUG,
    "error": logging.ERROR,
    "info": logging.INFO,
    "warn": logging.WARNING,
}


def _describe(request: PreparedRequest) -> str:
    method = (request.operation.method or "").upper()
    address = safe_address(request.address)
    return f"{method} {address}" if method else address


def _declared_headers(operation: OperationDescriptor) -> set[str]:
    names: set[str] = set()
    for requirement in operation.auth or ():
        schemes = (requirement,) if isinstance(requirement, AuthScheme) else requirement
        for scheme in schemes:
            if scheme.location == "header" and scheme.name:
                names.add(scheme.name.lower())
    return names


SECRET_HEADERS: list[str] = [
    "authorization",
    "cookie",
    "proxy-authorization",
    "set-cookie",
]


def _is_secret(name: str, declared: set[str]) -> bool:
    lower = name.lower()
    return (
        lower in SECRET_HEADERS
        or lower in declared
        or lower.endswith(("-key", "-token", "-secret"))
    )


def _safe_headers(
    headers: Mapping[str, str], operation: OperationDescriptor
) -> dict[str, str]:
    declared = _declared_headers(operation)
    return {
        name: "***" if _is_secret(name, declared) else value
        for name, value in headers.items()
    }


_ADDRESS = re.compile(r"""(?a:\b[a-z][a-z\d+.-]*://)[^\s\"'<>]+""", re.IGNORECASE)


def failure_text(error: BaseException) -> str:
    messages: list[str] = []
    seen: list[BaseException] = []
    current: BaseException | None = error
    while current is not None and not any(current is one for one in seen):
        seen.append(current)
        messages.append(str(current))
        current = current.__cause__
    return _ADDRESS.sub(
        lambda found: safe_address(found.group()), " Caused by: ".join(messages)
    )


class _CallLog:
    __slots__ = ("_at", "_id", "_label", "_request", "_sink", "_started")

    def __init__(
        self, log_id: str, request: PreparedRequest, sink: logging.Logger, at: int
    ) -> None:
        self._at = at
        self._id = log_id
        self._label = _describe(request)
        self._request = request
        self._sink = sink
        self._started = time.monotonic()

    def _write(self, level: int, text: str, *args: Any) -> None:
        if self._at <= level:
            spelled = f"[%s] %s {text}" if text else "[%s] %s"
            self._sink.log(level, spelled, self._id, self._label, *args)

    def _waited(self) -> int:
        return round((time.monotonic() - self._started) * 1000)

    def failed(self, error: BaseException) -> None:
        self._write(logging.ERROR, "failed: %s", failure_text(error))

    def replied(self, response: Any) -> None:
        waited = self._waited()
        if response is None:
            self._write(logging.INFO, "-> ? in %s ms", waited)
            return
        if getattr(response, "history", None):
            self._write(
                logging.WARNING, "was redirected to %s", safe_address(response.url)
            )
        self._write(logging.INFO, "-> %s in %s ms", response.status_code, waited)
        headers = _safe_headers(response.headers, self._request.operation)
        self._write(logging.DEBUG, "received %s in %s ms", headers, waited)

    def retrying(
        self, wait: float, retry: int, retries: int, after: Result | None = None
    ) -> None:
        again = f"retrying in {round(wait * 1000)} ms ({retry} of {retries})"
        if after is not None and after.response is not None:
            status = after.response.status_code
            self._write(logging.WARNING, "-> %s, %s", status, again)
        elif after is not None and after.error is not None:
            self._write(
                logging.WARNING, "failed: %s, %s", failure_text(after.error), again
            )
        else:
            self._write(logging.WARNING, "%s", again)

    def sending(self) -> None:
        self._started = time.monotonic()
        self._write(logging.INFO, "")
        headers = _safe_headers(self._request.meta, self._request.operation)
        self._write(logging.DEBUG, "sending %s", headers)


_LOGGER = logging.getLogger(__name__)


_HANDLER = logging.StreamHandler()


def _own_sink(at: int) -> logging.Logger:
    if not _LOGGER.hasHandlers():
        _LOGGER.addHandler(_HANDLER)
    if _LOGGER.level == logging.NOTSET or _LOGGER.level > at:
        _LOGGER.setLevel(at)
    return _LOGGER


def _read_level(named: str) -> str | None:
    spelled = named.lower()
    if spelled == "warning":
        return "warn"
    return spelled if spelled in LEVELS or spelled == "off" else None


class LoggerFeature(Feature):
    name = "logger"

    def __init__(
        self, level: str = "off", logger: logging.Logger | None = None
    ) -> None:
        self.level = level
        self.logger = logger
        self._ids = itertools.count(1)
        self._unknown: set[str] = set()
        self._warned: set[str] = set()

    def on_prepare(self, request: PreparedRequest, ctx: FeatureContext) -> None:
        named = str(request.options.get("log_level") or self.level or "off")
        level = _read_level(named)
        sink = request.options.get("logger") or self.logger
        if level is None and named not in self._unknown:
            self._unknown.add(named)
            (sink or _LOGGER).warning(
                'Unknown log level "%s": nothing is logged. Use "debug", "info", "warn", "error" or "off".',
                named,
            )
        if level is None or level == "off":
            return
        at = LEVELS[level]
        if sink is None:
            sink = _own_sink(at)
        log_id = f"req_{next(self._ids)}"
        request.log = _CallLog(log_id, request, sink, at)
        operation = request.operation
        if operation.deprecated and at <= logging.WARNING:
            method = (operation.method or "").upper()
            named = f"{method} {operation.address}" if method else operation.address
            if named not in self._warned:
                self._warned.add(named)
                sink.warning("[%s] %s is deprecated", log_id, named)

    def on_send(
        self, request: PreparedRequest, send: Send, ctx: FeatureContext
    ) -> Result:
        log = request.log
        if log is None:
            return send(request)
        result = send(request)
        log.replied(result.response)
        return result

    async def on_async_send(
        self, request: PreparedRequest, send: AsyncSend, ctx: FeatureContext
    ) -> Result:
        log = request.log
        if log is None:
            return await send(request)
        result = await send(request)
        log.replied(result.response)
        return result

    def on_error(
        self, error: BaseException, request: PreparedRequest, ctx: FeatureContext
    ) -> BaseException:
        if request.log is not None:
            request.log.failed(error)
        return error


LogLevel = Literal["debug", "error", "info", "off", "warn"]
"""How much a client logs. `'error'` writes failed calls. `'warn'` adds a retry
or a redirect. `'info'` adds a line per attempt, with its status and time.
`'debug'` adds headers, with credentials hidden.

"""
