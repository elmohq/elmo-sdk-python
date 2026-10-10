from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from typing import Any, Protocol, cast

from ...codec.json import dumped
from ...core.errors import empty_path_parameter
from ...core.types import SerializationDescriptor
from .encode import encode_component, encode_name


class BuildURL(Protocol):
    def __call__(
        self,
        *,
        address: str,
        base_url: str | None = None,
        path: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        serialization: SerializationDescriptor | None = None,
    ) -> str: ...


PATH_PARAM_RE = re.compile(r"\{[^{}]+\}")


ABSOLUTE_URL_RE = re.compile(r"^[a-z][a-z\d+.-]*://", re.IGNORECASE | re.ASCII)


def join_url(base_url: str | None, path: str) -> str:
    base = (base_url or "").partition("#")[0]
    kept, _, query = base.partition("?")
    if kept.endswith("/") and path.startswith("/"):
        path = path[1:]
    joined = kept + path
    if not query:
        return joined
    return f"{joined}{'&' if '?' in joined else '?'}{query}"


def address_url(address: str, base_url: str | None) -> str:
    absolute = bool(ABSOLUTE_URL_RE.match(address))
    path_url = address if absolute or address.startswith("/") else "/" + address
    return path_url if absolute else join_url(base_url, path_url)


def path_value(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ",".join(encode_component(item) for item in cast(Sequence[Any], value))
    if isinstance(value, dict):
        parts: list[str] = []
        for key, item in cast(dict[str, Any], value).items():
            parts.append(encode_component(key))
            parts.append(encode_component(item))
        return ",".join(parts)
    return encode_component(value)


def filled_url(address: str, base_url: str | None, path: dict[str, Any] | None) -> str:
    path = dumped(path)
    url = address_url(address, base_url)
    if path is None:
        return url

    def substitute(match: re.Match[str]) -> str:
        name = match.group()[1:-1]
        value = path.get(name)
        if value is None or value == "":
            raise empty_path_parameter(name, address)
        return path_value(value)

    return PATH_PARAM_RE.sub(substitute, url)


def with_query(url: str, query: dict[str, Any] | None) -> str:
    query = dumped(query)
    if not query:
        return url
    search: list[str] = []
    for name, value in query.items():
        if isinstance(value, dict):
            pairs: Iterable[tuple[str, Any]] = cast(dict[str, Any], value).items()
        elif isinstance(value, (list, tuple)):
            pairs = [(name, item) for item in cast(Sequence[Any], value)]
        else:
            pairs = [(name, value)]
        for key, item in pairs:
            if item is not None:
                search.append(f"{encode_name(key)}={encode_component(item)}")
    if not search:
        return url
    return f"{url}{'&' if '?' in url else '?'}{'&'.join(search)}"


def simple_url(
    *,
    address: str,
    base_url: str | None = None,
    path: dict[str, Any] | None = None,
    query: dict[str, Any] | None = None,
    serialization: SerializationDescriptor | None = None,
) -> str:
    return with_query(filled_url(address, base_url, path), query)
