from __future__ import annotations

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import AnyUrl, BaseModel, ConfigDict, Field

from .shared.pagination import Pagination


class RunSummary(BaseModel):
    """A single model answer, without its text. Fetch `prompts.runs.get()` for the
    answer itself."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, use_attribute_docstrings=True, extra="allow"
    )
    brand_id: str = Field(
        ..., validation_alias="brandId", serialization_alias="brandId"
    )
    brand_mentioned: bool = Field(
        ..., validation_alias="brandMentioned", serialization_alias="brandMentioned"
    )
    citation_count: int = Field(
        ..., validation_alias="citationCount", serialization_alias="citationCount"
    )
    competitors_mentioned: list[str] = Field(
        ...,
        validation_alias="competitorsMentioned",
        serialization_alias="competitorsMentioned",
    )
    created_at: datetime = Field(
        ..., validation_alias="createdAt", serialization_alias="createdAt"
    )
    id: UUID
    model: str
    prompt_id: UUID = Field(
        ..., validation_alias="promptId", serialization_alias="promptId"
    )
    provider: str | None
    """How the answer was obtained. Informational; not a stable enum."""
    web_queries: list[str] = Field(
        ..., validation_alias="webQueries", serialization_alias="webQueries"
    )
    """Searches the engine ran, where it exposes them."""
    web_search_enabled: bool = Field(
        ..., validation_alias="webSearchEnabled", serialization_alias="webSearchEnabled"
    )
    """Whether the engine answered with its own web search on."""


class RunCitation(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, use_attribute_docstrings=True, extra="allow"
    )
    citation_index: int = Field(
        ..., validation_alias="citationIndex", serialization_alias="citationIndex"
    )
    """Position within the answer's citation list."""
    domain: str
    title: str | None
    url: AnyUrl


class RunAnswer(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        use_attribute_docstrings=True, extra="allow"
    )
    text: str | None
    """The answer, normalized out of the provider's response. Null when nothing could be
    extracted."""


class Run(BaseModel):
    """One model answer with its normalized text and citations."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, use_attribute_docstrings=True, extra="allow"
    )
    answer: RunAnswer
    brand_id: str = Field(
        ..., validation_alias="brandId", serialization_alias="brandId"
    )
    brand_mentioned: bool = Field(
        ..., validation_alias="brandMentioned", serialization_alias="brandMentioned"
    )
    citation_count: int = Field(
        ..., validation_alias="citationCount", serialization_alias="citationCount"
    )
    citations: list[RunCitation]
    competitors_mentioned: list[str] = Field(
        ...,
        validation_alias="competitorsMentioned",
        serialization_alias="competitorsMentioned",
    )
    created_at: datetime = Field(
        ..., validation_alias="createdAt", serialization_alias="createdAt"
    )
    id: UUID
    model: str
    prompt_id: UUID = Field(
        ..., validation_alias="promptId", serialization_alias="promptId"
    )
    provider: str | None
    """How the answer was obtained. Informational; not a stable enum."""
    web_queries: list[str] = Field(
        ..., validation_alias="webQueries", serialization_alias="webQueries"
    )
    """Searches the engine ran, where it exposes them."""
    web_search_enabled: bool = Field(
        ..., validation_alias="webSearchEnabled", serialization_alias="webSearchEnabled"
    )
    """Whether the engine answered with its own web search on."""


class RunList(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="allow")
    data: list[RunSummary]
    pagination: Pagination


GetRunResponse = Run
"""Get a run"""
