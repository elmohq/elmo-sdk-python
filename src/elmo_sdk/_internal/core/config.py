from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from .metadata import merge_metadata


def fold_retry(
    sources: Sequence[dict[str, Any] | None], merged: dict[str, Any]
) -> dict[str, Any]:
    if not any(source and source.get("retry") is not None for source in sources):
        return merged
    retry: Any = None
    for source in sources:
        own = source.get("retry") if source else None
        count = source.get("max_retries") if source else None
        counted = isinstance(count, int) and not isinstance(count, bool)
        if own is False:
            retry = False
        elif own is not None or counted:
            rules: dict[str, Any] = {
                **(cast(dict[str, Any], retry) if isinstance(retry, dict) else {}),
                **(cast(dict[str, Any], own) if isinstance(own, dict) else {}),
            }
            if counted and not (isinstance(own, dict) and "max_retries" in own):
                rules["max_retries"] = count
            retry = rules
    merged["retry"] = retry
    merged.pop("max_retries", None)
    return merged


MERGED_LAYERS = ("path", "query")


def merge_layers(
    sources: Sequence[dict[str, Any] | None], merged: dict[str, Any]
) -> dict[str, Any]:
    for layer in MERGED_LAYERS:
        combined: dict[str, Any] = {}
        found = False
        for source in sources:
            named = source.get(layer) if source else None
            if isinstance(named, dict):
                combined.update(cast(dict[str, Any], named))
                found = True
        if found:
            merged[layer] = combined
    return merged


def merge_configs(*sources: dict[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for source in sources:
        if not source:
            continue
        merged.update(source)
    merged["headers"] = merge_metadata(
        *[source.get("headers") if source else None for source in sources]
    )
    return fold_retry(sources, merge_layers(sources, merged))


def create_config(**overrides: Any) -> dict[str, Any]:
    return merge_configs({"headers": {}}, overrides)


def base_url_of(options: dict[str, Any], fallback: str | None = None) -> str | None:
    stated: str | None = options.get("base_url")
    return fallback if stated is None else stated
