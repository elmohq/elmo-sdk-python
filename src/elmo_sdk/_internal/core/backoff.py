from __future__ import annotations

import math
import random
import re
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal

Jitter = bool | float | Literal["equal", "full", "none"]
"""How much of each wait is random, so callers that failed together do not all
come back at once.

A number from 0 to 1 is the random share: `0.25` waits between three quarters
of the computed wait and all of it. `full` is 1, `equal` is 0.5 and `none` is
0. `True` is `full` and `False` is `none`.
"""


@dataclass(frozen=True)
class RetryAfterHeader:
    """A header the API may name its own wait in, and how to read its value."""

    name: str
    """Header name, matched case-insensitively."""
    kind: str = "duration"
    """Whether a number counts forward from now, or names a moment."""
    unit: str = "second"
    """What a number in this header counts in."""


RETRY_AFTER = RetryAfterHeader(name="retry-after")


RETRY_AFTER_HEADERS: list[RetryAfterHeader] = [
    RetryAfterHeader(name="retry-after-ms", unit="millisecond"),
    RETRY_AFTER,
    RetryAfterHeader(name="x-ratelimit-reset-after"),
    RetryAfterHeader(name="x-ratelimit-reset", kind="moment"),
    RetryAfterHeader(name="x-rate-limit-reset", kind="moment"),
]


_ASCTIME = re.compile(
    r"[a-z]{3} ([a-z]{3}) +(\d\d?) (\d\d:\d\d:\d\d) (\d{4})", re.IGNORECASE | re.ASCII
)


_MOMENT = re.compile(
    r"(?:(\d{4})-(\d\d)-(\d\d)[t ]|(?:[a-z]+, ?)?(\d\d?)[ -]([a-z]{3})[ -](\d\d|\d{4}) )(\d\d):(\d\d)(?::(\d\d)(?:\.(\d{1,3})\d*)?)? ?(z|gmt|utc?|[+-](?:[01]\d|2[0-3]):?[0-5]\d)",
    re.IGNORECASE | re.ASCII,
)


_MONTHS = "janfebmaraprmayjunjulaugsepoctnovdec"


def _moment(value: str, now: float) -> float | None:
    text = value.strip(" 	")
    asctime = _ASCTIME.fullmatch(text)
    match = _MOMENT.fullmatch(asctime.expand(r"\2 \1 \4 \3 GMT") if asctime else text)
    if match is None:
        return None
    groups = match.groups()
    iso_year, iso_month, iso_day, day, name, year = groups[:6]
    hour, minute, second, ms, zone = groups[6:]
    index = _MONTHS.find((name or "").lower())
    if not iso_month and index % 3:
        return None
    full = int(year or iso_year)
    if len(year or "") == 2:
        present = datetime.fromtimestamp(now, tz=timezone.utc).year
        full += present - present % 100
        full -= 100 if full > present + 50 else 0
    leap = 1 if second == "60" else 0
    try:
        stated = datetime(
            full,
            int(iso_month) if iso_month else index // 3 + 1,
            int(day or iso_day),
            int(hour),
            int(minute),
            int(second or 0) - leap,
            int((ms or "").ljust(3, "0")) * 1000,
            tzinfo=timezone.utc,
        )
    except ValueError:
        return None
    digits = zone.replace(":", "")
    offset = int(digits[1:3]) * 3600 + int(digits[3:]) * 60 if len(digits) == 5 else 0
    return stated.timestamp() + leap - (-offset if digits[0] == "-" else offset)


_NUMBER = re.compile(r"[0-9]+(?:\.[0-9]+)?")


def parse_retry_after(
    value: str | None, header: RetryAfterHeader = RETRY_AFTER, now: float = 0.0
) -> float | None:
    if not value:
        return None
    text = value.strip(" 	")
    if not _NUMBER.fullmatch(text):
        stated = _moment(text, now)
        return None if stated is None else max(0.0, stated - now)
    number = float(text)
    seconds = number / 1000 if header.unit == "millisecond" else number
    return max(0.0, seconds - now if header.kind == "moment" else seconds)


def retry_after_delay(
    response: Any, headers: list[RetryAfterHeader] | None = None, now: float = 0.0
) -> float | None:
    meta: Mapping[str, str] = getattr(response, "headers", None) or {}
    sent = _moment(meta.get("date") or "", now)
    clock = now if sent is None else sent

    for header in headers if headers is not None else RETRY_AFTER_HEADERS:
        delay = parse_retry_after(meta.get(header.name), header, clock)
        if delay is not None:
            return delay
    return None


TIMER_LIMIT = threading.TIMEOUT_MAX


BACKOFF_DELAY = 0.5


BACKOFF_MAX_DELAY = 30.0


MAX_RETRY_AFTER = 60.0


def exceeds_max_retry_after(
    delay: float | None, max_delay: float = MAX_RETRY_AFTER
) -> bool:
    return delay is not None and delay > max_delay


def jitter_share(jitter: Jitter) -> float:
    if isinstance(jitter, bool):
        return 1.0 if jitter else 0.0
    if isinstance(jitter, (int, float)):
        return min(1.0, max(0.0, float(jitter)))
    if jitter == "equal":
        return 0.5
    return 1.0 if jitter == "full" else 0.0


def backoff_delay(
    retry: int,
    delay: float = BACKOFF_DELAY,
    max_delay: float = BACKOFF_MAX_DELAY,
    jitter: Jitter = True,
    strategy: str = "exponential",
) -> float:
    try:
        growth = delay if strategy == "constant" or not delay else delay * 2.0**retry
    except OverflowError:
        growth = math.inf
    capped = min(growth, max_delay)
    share = jitter_share(jitter)
    if not share:
        return capped
    return capped * (1 - share) + random.random() * capped * share
