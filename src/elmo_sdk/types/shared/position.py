from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field


class SentimentSummary(BaseModel):
    """**Experimental — the shape may still change.**

    Answers that mention the company, by the mention judge's sentiment toward it. An
    answer that only links to the company counts in none. All zero for history the judge
    hasn't re-judged yet. Counted over every answer in the window, unlike
    `visibility.current` and the share-of-voice `mentions` and `share`, which count each
    prompt's latest result.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, use_attribute_docstrings=True, extra="allow"
    )
    mixed: Annotated[int, Field(ge=0)]
    negative: Annotated[int, Field(ge=0)]
    negative_share: float | None = Field(
        ..., validation_alias="negativeShare", serialization_alias="negativeShare"
    )
    """Negative answers as a fraction of those with a sentiment (the four counts). Ratio
    0–1; null when there are none."""
    neutral: Annotated[int, Field(ge=0)]
    positive: Annotated[int, Field(ge=0)]
    positive_share: float | None = Field(
        ..., validation_alias="positiveShare", serialization_alias="positiveShare"
    )
    """Positive answers as a fraction of those with a sentiment (the four counts). Ratio
    0–1; null when there are none."""


class Position(BaseModel):
    """**Experimental — the shape may still change.**

    The company's position among the tracked companies the answers name, 1 being named
    first. Companies that aren't tracked aren't ranked. Counted over every answer in the
    window, unlike `visibility.current` and the share-of-voice `mentions` and `share`,
    which count each prompt's latest result.
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        use_attribute_docstrings=True, extra="allow"
    )
    average: float | None
    """Average position to one decimal; null when no answer ranks it."""
