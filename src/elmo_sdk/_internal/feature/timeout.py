from __future__ import annotations

from typing import Any

from ..core.errors import unsendable_timeout
from ..core.features import Feature
from ..core.types import CallTimeout, FeatureContext, OperationDescriptor

DEFAULT_TIMEOUT: float = 60.0


def _is_limit(limit: Any) -> bool:
    if limit is None or limit is False:
        return True
    if isinstance(limit, (int, float)):
        return not isinstance(limit, bool) and limit >= 0
    return hasattr(limit, "connect") and hasattr(limit, "read")


def _operation_key(operation: OperationDescriptor) -> str:
    method = operation.method
    return f"{method.upper()} {operation.address}" if method else operation.address


class TimeoutFeature(Feature):
    name = "timeout"

    def __init__(self, seconds: float = DEFAULT_TIMEOUT) -> None:
        self.seconds = seconds

    def on_options(
        self,
        options: dict[str, Any],
        operation: OperationDescriptor,
        ctx: FeatureContext,
    ) -> None:
        handed: CallTimeout | None = (
            self.seconds if operation.timeout is None else operation.timeout
        )
        limit = options.get("timeout")
        if callable(limit):
            chosen = limit(_operation_key(operation), handed)
            limit = handed if chosen is None else chosen
        elif limit is None:
            limit = handed
        if not _is_limit(limit):
            raise unsendable_timeout(limit)
        options["timeout"] = limit
