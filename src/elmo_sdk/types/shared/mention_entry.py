from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class MentionEntry(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        use_attribute_docstrings=True, extra="allow"
    )
    count: int
    """Number of runs where this entity was mentioned"""
    entity: str
    """Competitor entity name"""


class MentionsSummary(BaseModel):
    """Aggregated mention counts for a prompt across its evaluation runs."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, use_attribute_docstrings=True, extra="allow"
    )
    brand_mentions_total: int = Field(
        ...,
        validation_alias="brandMentionsTotal",
        serialization_alias="brandMentionsTotal",
    )
    """Number of runs where the brand was mentioned"""
    competitor_mentions_total: int = Field(
        ...,
        validation_alias="competitorMentionsTotal",
        serialization_alias="competitorMentionsTotal",
    )
    """Total count of individual competitor mentions across all runs (a single run
    mentioning 3 competitors counts as 3)"""
    mentions_top_k: list[MentionEntry] = Field(
        ..., validation_alias="mentionsTopK", serialization_alias="mentionsTopK"
    )
    """Top-K competitor entities ranked by mention count"""
    mentions_total: int = Field(
        ..., validation_alias="mentionsTotal", serialization_alias="mentionsTotal"
    )
    """Total brand + competitor mentions across all runs"""
