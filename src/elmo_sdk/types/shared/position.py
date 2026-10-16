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
        use_attribute_docstrings=True, extra="allow"
    )
    mixed: Annotated[int, Field(ge=0)]
    negative: Annotated[int, Field(ge=0)]
    neutral: Annotated[int, Field(ge=0)]
    positive: Annotated[int, Field(ge=0)]
    score: float | None
    """Net sentiment of the answers with a sentiment: positive counts 1, neutral and
    mixed 0.5, negative 0, averaged. 0.5 means neutral on balance. Ratio 0–1; null when
    there are none."""


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
