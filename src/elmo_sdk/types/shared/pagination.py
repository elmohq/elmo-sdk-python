from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class Pagination(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, use_attribute_docstrings=True, extra="allow"
    )
    limit: int
    page: int
    total: int
    """Total items matching the request."""
    total_pages: int = Field(
        ..., validation_alias="totalPages", serialization_alias="totalPages"
    )
