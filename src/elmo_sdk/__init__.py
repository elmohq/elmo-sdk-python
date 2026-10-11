from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._internal.binding.rest.errors import (
        AuthenticationError,
        BadRequestError,
        ConflictError,
        InternalServerError,
        NotFoundError,
        PaymentRequiredError,
        PermissionDeniedError,
        RateLimitError,
        UnprocessableEntityError,
    )
    from ._internal.core.backoff import Jitter, RetryAfterHeader
    from ._internal.core.errors import (
        APIError,
        DecodeError,
        ElmoError,
        FailureBody,
        MissingCredentialError,
        TransportError,
        TransportTimeoutError,
    )
    from ._internal.core.missing import MISSING, Missing
    from ._internal.core.page import AsyncPage, Page
    from ._internal.core.response import Response
    from ._internal.core.types import (
        AsyncAuthResolver,
        AsyncAuthValue,
        AsyncCredentialValue,
        AuthResolver,
        AuthScheme,
        AuthToken,
        AuthValue,
        CallTimeout,
        CredentialValue,
        PhasedTimeout,
        PreparedRequest,
        RawResponse,
        Result,
        RetryOptions,
        RetryValue,
        TimeoutPolicy,
        TimeoutValue,
    )
    from ._internal.feature.interceptors import (
        ErrorHook,
        Interceptors,
        RequestHook,
        ResponseHook,
    )
    from ._internal.feature.logger import LogLevel
    from ._internal.transport.httpx import AsyncHttpxLike, HttpxLike
    from .client import AsyncElmo, Elmo, __version__
    from .resources.shared.request_options import AsyncRequestOptions, RequestOptions

__all__ = [
    "MISSING",
    "APIError",
    "AsyncAuthResolver",
    "AsyncAuthValue",
    "AsyncCredentialValue",
    "AsyncElmo",
    "AsyncHttpxLike",
    "AsyncPage",
    "AsyncRequestOptions",
    "AuthResolver",
    "AuthScheme",
    "AuthToken",
    "AuthValue",
    "AuthenticationError",
    "BadRequestError",
    "CallTimeout",
    "ConflictError",
    "CredentialValue",
    "DecodeError",
    "Elmo",
    "ElmoError",
    "ErrorHook",
    "FailureBody",
    "HttpxLike",
    "Interceptors",
    "InternalServerError",
    "Jitter",
    "LogLevel",
    "Missing",
    "MissingCredentialError",
    "NotFoundError",
    "Page",
    "PaymentRequiredError",
    "PermissionDeniedError",
    "PhasedTimeout",
    "PreparedRequest",
    "RateLimitError",
    "RawResponse",
    "RequestHook",
    "RequestOptions",
    "Response",
    "ResponseHook",
    "Result",
    "RetryAfterHeader",
    "RetryOptions",
    "RetryValue",
    "TimeoutPolicy",
    "TimeoutValue",
    "TransportError",
    "TransportTimeoutError",
    "UnprocessableEntityError",
    "__version__",
]


_LAZY_EXPORTS = {
    "APIError": ("._internal.core.errors", "APIError"),
    "AsyncAuthResolver": ("._internal.core.types", "AsyncAuthResolver"),
    "AsyncAuthValue": ("._internal.core.types", "AsyncAuthValue"),
    "AsyncCredentialValue": ("._internal.core.types", "AsyncCredentialValue"),
    "AsyncElmo": (".client", "AsyncElmo"),
    "AsyncHttpxLike": ("._internal.transport.httpx", "AsyncHttpxLike"),
    "AsyncPage": ("._internal.core.page", "AsyncPage"),
    "AsyncRequestOptions": (".resources.shared.request_options", "AsyncRequestOptions"),
    "AuthResolver": ("._internal.core.types", "AuthResolver"),
    "AuthScheme": ("._internal.core.types", "AuthScheme"),
    "AuthToken": ("._internal.core.types", "AuthToken"),
    "AuthValue": ("._internal.core.types", "AuthValue"),
    "AuthenticationError": ("._internal.binding.rest.errors", "AuthenticationError"),
    "BadRequestError": ("._internal.binding.rest.errors", "BadRequestError"),
    "CallTimeout": ("._internal.core.types", "CallTimeout"),
    "ConflictError": ("._internal.binding.rest.errors", "ConflictError"),
    "CredentialValue": ("._internal.core.types", "CredentialValue"),
    "DecodeError": ("._internal.core.errors", "DecodeError"),
    "Elmo": (".client", "Elmo"),
    "ElmoError": ("._internal.core.errors", "ElmoError"),
    "ErrorHook": ("._internal.feature.interceptors", "ErrorHook"),
    "FailureBody": ("._internal.core.errors", "FailureBody"),
    "HttpxLike": ("._internal.transport.httpx", "HttpxLike"),
    "Interceptors": ("._internal.feature.interceptors", "Interceptors"),
    "InternalServerError": ("._internal.binding.rest.errors", "InternalServerError"),
    "Jitter": ("._internal.core.backoff", "Jitter"),
    "LogLevel": ("._internal.feature.logger", "LogLevel"),
    "MISSING": ("._internal.core.missing", "MISSING"),
    "Missing": ("._internal.core.missing", "Missing"),
    "MissingCredentialError": ("._internal.core.errors", "MissingCredentialError"),
    "NotFoundError": ("._internal.binding.rest.errors", "NotFoundError"),
    "Page": ("._internal.core.page", "Page"),
    "PaymentRequiredError": ("._internal.binding.rest.errors", "PaymentRequiredError"),
    "PermissionDeniedError": (
        "._internal.binding.rest.errors",
        "PermissionDeniedError",
    ),
    "PhasedTimeout": ("._internal.core.types", "PhasedTimeout"),
    "PreparedRequest": ("._internal.core.types", "PreparedRequest"),
    "RateLimitError": ("._internal.binding.rest.errors", "RateLimitError"),
    "RawResponse": ("._internal.core.types", "RawResponse"),
    "RequestHook": ("._internal.feature.interceptors", "RequestHook"),
    "RequestOptions": (".resources.shared.request_options", "RequestOptions"),
    "Response": ("._internal.core.response", "Response"),
    "ResponseHook": ("._internal.feature.interceptors", "ResponseHook"),
    "Result": ("._internal.core.types", "Result"),
    "RetryAfterHeader": ("._internal.core.backoff", "RetryAfterHeader"),
    "RetryOptions": ("._internal.core.types", "RetryOptions"),
    "RetryValue": ("._internal.core.types", "RetryValue"),
    "TimeoutPolicy": ("._internal.core.types", "TimeoutPolicy"),
    "TimeoutValue": ("._internal.core.types", "TimeoutValue"),
    "TransportError": ("._internal.core.errors", "TransportError"),
    "TransportTimeoutError": ("._internal.core.errors", "TransportTimeoutError"),
    "UnprocessableEntityError": (
        "._internal.binding.rest.errors",
        "UnprocessableEntityError",
    ),
    "__version__": (".client", "__version__"),
}


if not TYPE_CHECKING:

    def __getattr__(name: str) -> object:
        if name not in _LAZY_EXPORTS:
            raise AttributeError(f"module {__name__} has no attribute {name}")
        module, attribute = _LAZY_EXPORTS[name]
        value = getattr(import_module(module, __name__), attribute)
        globals()[name] = value
        return value


def __dir__() -> list[str]:
    return list(__all__)
