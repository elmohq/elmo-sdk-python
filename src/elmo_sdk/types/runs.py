from __future__ import annotations

from datetime import datetime
from typing import Annotated, ClassVar
from uuid import UUID

from pydantic import AnyUrl, BaseModel, ConfigDict, Field

from .shared.common import OpenEnum
from .shared.pagination import Pagination


class MentionAssessmentSentiment(str, OpenEnum):
    """The likeliest sentiment toward this company in the passages about it. Null when
    the answer isn't about it, or when it only links to the company."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class MentionAssessment(BaseModel):
    """**Experimental — the shape may still change.**

    The mention judge's assessment of one brand or competitor named in an answer.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, use_attribute_docstrings=True, extra="allow"
    )
    mention_count: int | None = Field(
        ..., validation_alias="mentionCount", serialization_alias="mentionCount"
    )
    """How many times the answer mentions it. Null when the answer isn't counted as
    mentioning it."""
    mentioned: bool
    """Whether the answer counts as mentioning this company. A name the judge can't call
    either way counts."""
    position: int | None
    """1 for the tracked company the answer names first, 2 for the next, and so on. Null
    when the answer isn't counted as mentioning it."""
    probability: Annotated[float, Field(ge=0, le=1)]
    """Calibrated probability that the answer mentions this company."""
    reason: str | None
    """When it isn't counted as a mention, the likeliest other reading: `other_meaning`
    (the name used as an ordinary word), `other_company` (a different company with the
    same name) or `no_info` (the answer says it knows nothing about it). Informational;
    not a stable enum."""
    sentiment: MentionAssessmentSentiment | None
    """The likeliest sentiment toward this company in the passages about it. Null when
    the answer isn't about it, or when it only links to the company."""
    sentiment_probabilities: dict[str, float] | None = Field(
        ...,
        validation_alias="sentimentProbabilities",
        serialization_alias="sentimentProbabilities",
    )
    """Probability of each sentiment, keyed by label."""


class RunAssessments(BaseModel):
    """**Experimental — the shape may still change.**

    The mention judge's assessments for one answer. Null when the run's mentions were
    matched by name, before the judge, until a replay judges it.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        use_attribute_docstrings=True, extra="allow"
    )
    brand: MentionAssessment | None
    """Null when the answer never names the brand."""
    competitors: dict[str, MentionAssessment]
    """Keyed by competitor name; only competitors the answer names."""


class RunSummary(BaseModel):
    """A single model answer, without its text. Fetch `prompts.runs.get()` for the
    answer itself."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, use_attribute_docstrings=True, extra="allow"
    )
    assessments: RunAssessments | None
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
    assessments: RunAssessments | None
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
