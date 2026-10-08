from __future__ import annotations

import json
import numbers
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from decimal import Decimal
from enum import Enum
from ipaddress import IPv4Address, IPv6Address
from typing import Any, TypeGuard, cast
from uuid import UUID

from ..core.errors import ElmoError
from ..core.types import EncodedBody


def is_mapping(value: Any) -> TypeGuard[Mapping[Any, Any]]:
    return isinstance(value, Mapping)


def is_sequence(value: Any) -> bool:
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return False
    return isinstance(value, Sequence)


def iso_duration(value: timedelta) -> str:
    sign = "-" if value < timedelta(0) else ""
    value = abs(value)
    hours, rest = divmod(value.seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    clock = ""
    if hours:
        clock += f"{hours}H"
    if minutes:
        clock += f"{minutes}M"
    if value.microseconds:
        clock += f"{seconds}.{value.microseconds:06d}".rstrip("0") + "S"
    elif seconds or not (value.days or clock):
        clock += f"{seconds}S"
    days = f"{value.days}D" if value.days else ""
    return f"{sign}P{days}T{clock}" if clock else f"{sign}P{days}"


def type_name(value: Any) -> str:
    kind: type[Any] = value.__class__
    if kind.__module__ == "builtins":
        return kind.__qualname__
    return f"{kind.__module__}.{kind.__qualname__}"


def as_json(value: Any) -> Any:
    dump = getattr(value, "model_dump", None)
    if dump is not None:
        return dump(by_alias=True, exclude_unset=True, mode="json")
    serializer = getattr(value.__class__, "__pydantic_serializer__", None)
    if serializer is not None:
        return serializer.to_python(value, mode="json")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (date, time)):
        return value.isoformat()
    if isinstance(value, timedelta):
        return iso_duration(value)
    if isinstance(value, (Decimal, IPv4Address, IPv6Address, UUID)):
        return str(value)
    if is_mapping(value):
        return dict(value)
    if isinstance(value, (set, frozenset)) or is_sequence(value):
        return list(cast(Iterable[Any], value))
    if isinstance(value, numbers.Integral):
        return int(value)
    if isinstance(value, numbers.Real):
        return float(value)
    raise ElmoError(f"A value of type {type_name(value)} cannot be written as JSON.")


def json_text(value: Any) -> str:
    try:
        return json.dumps(
            value,
            allow_nan=False,
            default=as_json,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    except (RecursionError, TypeError, ValueError) as error:
        if str(error).startswith("Out of range float values"):
            raise ElmoError("NaN and Infinity cannot be written as JSON.") from None
        raise ElmoError(f"A value cannot be written as JSON: {error}") from error


@dataclass
class JSONCodec:
    media_types: list[str] = field(default_factory=lambda: ["application/json"])
    name: str = "json"

    def encode(self, value: Any) -> EncodedBody:
        return EncodedBody(
            payload=json_text(value).encode("utf-8"), content_type="application/json"
        )


json_codec = JSONCodec()


def dumped(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return as_json(value)
    if is_mapping(value):
        return {key: dumped(item) for key, item in value.items()}
    if is_sequence(value):
        return [dumped(item) for item in cast(Sequence[Any], value)]
    return value
