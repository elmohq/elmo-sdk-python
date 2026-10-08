from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class Error(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        use_attribute_docstrings=True, extra="allow"
    )
    code: str | None = None
    """Stable machine-readable code. Deliberately not an enum: new values are added
    without a version bump, so treat an unrecognized one as its HTTP status implies.
    Currently: `unauthorized`, `insufficient_scope`, `forbidden`, `not_found`,
    `validation_error`, `conflict`, `rate_limited`, `method_not_allowed`, `read_only`,
    `no_active_plan`, `brand_limit`, `prompt_limit`, `model_not_in_plan`,
    `model_picks_exceeded`, `premium_not_in_plan`, `premium_pool_exhausted`,
    `cadence_faster_than_plan`, `internal_error`."""
    error: str
    """Error type"""
    message: str | None = None
    """Detailed error message"""
