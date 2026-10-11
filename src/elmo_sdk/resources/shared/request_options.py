from __future__ import annotations

from logging import Logger
from typing import Any, TypedDict

from ..._internal.core.types import (
    AsyncAuthValue,
    AsyncCredentialValue,
    AuthValue,
    CredentialValue,
    RetryValue,
    TimeoutValue,
)
from ..._internal.feature.interceptors import Interceptors
from ..._internal.feature.logger import LogLevel


class _BaseRequestOptions(TypedDict, total=False):
    base_url: str
    """The base URL for this call, in place of the client's."""
    extra_body: dict[str, Any]
    """Fields to add to the request body, for one this version does not
    declare. Merged over the body's own fields.
    """
    extra_headers: dict[str, str]
    """Headers to send. Merged per name, and `None` drops one."""
    extra_path: dict[str, Any]
    """Path parameters. Merged per name."""
    extra_query: dict[str, Any]
    """Query parameters to add. Merged per name, and `None` drops one."""
    interceptors: Interceptors
    """Run your own hooks around every call. Each is a sequence of callables,
    which the awaited client also waits for.

    `request` reads the request after the credentials are on it and before
    it is sent. `response` and `error` each return what the caller reads, so
    a hook that only observes returns what it was given.
    """
    log_level: LogLevel
    """Set the log level. Raise it to see what each call sent and what came
    back. `'debug'` adds headers, with credentials hidden.

    Read from the `ELMO_LOG` environment variable when unset.

    Defaults to `'off'`.
    """
    logger: Logger
    """Set the logger. This SDK's own `logging.Logger` by default, which writes
    to standard error unless the application has given it a handler of its
    own.
    """
    max_retries: int
    """The maximum number of times a failed call is sent again.

    The same count as `retry["max_retries"]`, which wins where both are set.
    It counts retries and nothing else: `retry` decides which failures are
    retried.

    Defaults to `2`.
    """
    request_body: Any
    """The request body, before it is encoded."""
    retry: RetryValue
    """How a failed call is retried, or `False` to send it once.

    Defaults to `{"max_retries": 2}`.
    """
    timeout: TimeoutValue
    """The maximum time one attempt may run.

    Set `False` or `0` for no limit, or a function that returns the limit of
    one call. It is given the operation as `METHOD /path` and the limit the
    call would otherwise get.

    Defaults to `60`.

    The unit is seconds.
    """


class RequestOptions(_BaseRequestOptions, total=False):
    """What one call may set for itself, overriding the client it goes through."""

    api_key: CredentialValue
    """An instance admin key from `ADMIN_API_KEYS`, or an organization key
    (`elmo_…`) issued from the dashboard. Its value starts with `elmo_`.

    Read from the `ELMO_API_KEY` environment variable when unset.
    """
    auth: AuthValue
    """Decides each credential a call sends, given the scheme and the value its
    option holds. What it returns is sent, so return the value to keep it.
    `False` sends no credential.
    """


class AsyncRequestOptions(_BaseRequestOptions, total=False):
    """What one call may set for itself, overriding the client it goes through."""

    api_key: AsyncCredentialValue
    """An instance admin key from `ADMIN_API_KEYS`, or an organization key
    (`elmo_…`) issued from the dashboard. Its value starts with `elmo_`.

    Read from the `ELMO_API_KEY` environment variable when unset.
    """
    auth: AsyncAuthValue
    """Decides each credential a call sends, given the scheme and the value its
    option holds. What it returns is sent, so return the value to keep it.
    `False` sends no credential.
    """
