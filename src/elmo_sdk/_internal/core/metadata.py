from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, cast

from ..codec.json import dumped, is_mapping
from .text import to_text
from .types import Metadata


def metadata_text(value: Any) -> str:
    written = dumped(value)
    if is_mapping(written):
        pairs = written.items()
        written = [one for pair in pairs if pair[1] is not None for one in pair]
    if isinstance(written, list):
        return ",".join(to_text(item) for item in cast(Sequence[Any], written))
    return to_text(written)


def merge_metadata(*sources: Mapping[str, Any] | None) -> Metadata:
    merged: Metadata = {}
    for source in sources:
        if not source:
            continue
        for key, value in source.items():
            name = key.lower()
            if value is None:
                merged.pop(name, None)
            else:
                merged[name] = metadata_text(value)
    return merged


FIELD_VALUE = re.compile(r"[\t\x20-\x7e\x80-\xff]*")


def is_field_value(value: str) -> bool:
    return FIELD_VALUE.fullmatch(value) is not None


def unsendable_name(meta: Metadata) -> str | None:
    for name, value in meta.items():
        if not is_field_value(value):
            return name
    return None


def stack_metadata(*sources: Mapping[str, Any] | None) -> dict[str, str | None]:
    stacked: dict[str, str | None] = {}
    for source in sources:
        for key, value in (source or {}).items():
            stacked[key.lower()] = None if value is None else metadata_text(value)
    return stacked
