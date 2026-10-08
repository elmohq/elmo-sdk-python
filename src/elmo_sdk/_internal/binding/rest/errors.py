from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any

from ...core.errors import APIError, DecodeError, safe_address
from ...core.types import RawResponse

if TYPE_CHECKING:
    from ....types.shared.error import Error


def unreadable_body(
    response: RawResponse, cause: BaseException | None = None
) -> DecodeError:
    url = getattr(response, "url", "") or ""
    where = f' for "{safe_address(url)}"' if url else ""
    headers: Mapping[str, str] = getattr(response, "headers", None) or {}
    content_type = headers.get("content-type")
    said = f' Its content type said "{content_type}".' if content_type else ""
    error = DecodeError(
        f"The API answered {response.status_code}{where} with a body this client could not read.{said}",
        response=response,
    )
    error.__cause__ = cause
    return error


class BadRequestError(APIError["Error"]):
    """The API could not read the request, so it did not act on it."""

    data: Error | None


class AuthenticationError(APIError["Error"]):
    """No usable credential reached the API: it was missing, unreadable, or rejected."""

    data: Error | None


class PaymentRequiredError(APIError["Error"]):
    """The plan or the quota on this account does not cover the call."""

    data: Error | None


class PermissionDeniedError(APIError["Error"]):
    """The credential was accepted, but it does not grant this call."""

    data: Error | None


class NotFoundError(APIError["Error"]):
    """Nothing is at this address, or the credential may not see what is."""

    data: Error | None


class ConflictError(APIError["Error"]):
    """The call collided with the resource's current state: a duplicate, or a concurrent
    change.
    """

    data: Error | None


class UnprocessableEntityError(APIError):
    """The request was read, and its contents were rejected."""


class RateLimitError(APIError["Error"]):
    """Too many calls. `retry_after_seconds` carries how long the API asked to wait."""

    data: Error | None


APIErrorClass = Callable[..., APIError]


BY_STATUS: dict[int, APIErrorClass] = {
    400: BadRequestError,
    401: AuthenticationError,
    402: PaymentRequiredError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: RateLimitError,
}


class InternalServerError(APIError["Error"]):
    """The API failed after accepting the call. Every status from 500 up arrives as
    this.
    """

    data: Error | None


def to_api_error(
    status: int,
    body: Any,
    response: RawResponse,
    unauthenticated: Callable[[], str] | None = None,
) -> APIError:
    failure = BY_STATUS.get(status) or (
        InternalServerError if status >= 500 else APIError
    )
    note = unauthenticated() if unauthenticated and status in (401, 403) else None
    return failure(status, body, response, note)
