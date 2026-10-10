from __future__ import annotations

from datetime import date, time, timedelta
from enum import Enum
from typing import Any


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


def to_text(value: Any) -> str:
    if isinstance(value, Enum):
        value = value.value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (date, time)):
        return value.isoformat()
    if isinstance(value, timedelta):
        return iso_duration(value)
    return value if isinstance(value, str) else str(value)
