from __future__ import annotations

import functools
from collections.abc import Mapping
from typing import Any, cast

from .errors import unsendable_input
from .missing import MISSING


def group_params(fields: list[dict[str, Any]], /, **values: Any) -> dict[str, Any]:
    named = {field["key"]: field for field in fields}
    grouped: dict[str, Any] = {}

    for key, value in values.items():
        field = named.get(key)
        option = field.get("option") if field else None
        if option is not None and value is MISSING:
            grouped[option] = MISSING
            continue
        if value is MISSING or option is not None and value is None:
            continue
        if field is None:
            grouped[key] = value
            continue
        if field.get("whole"):
            grouped["body"] = value
            continue
        slot = grouped.setdefault(field["in"], {})
        slot[field.get("map") or key] = value
    return grouped


LAYERS = ("path", "query")


def merge_params(inputs: dict[str, Any], options: Mapping[str, Any]) -> dict[str, Any]:
    merged = {**inputs, **options}
    for layer in LAYERS:
        named = inputs.get(layer)
        given = options.get(layer)
        if isinstance(named, dict) and isinstance(given, dict):
            merged[layer] = {**named, **given}
    return merged


def keyword_options(options: Mapping[str, Any], known: Any) -> Mapping[str, Any]:
    names: frozenset[str] = known.__optional_keys__
    for name in options:
        if name not in names:
            raise TypeError(f"got an unexpected keyword argument '{name}'")
    return options


EXTRAS: Mapping[str, str] = {
    "extra_cookies": "cookies",
    "extra_headers": "headers",
    "extra_path": "path",
    "extra_query": "query",
    "request_body": "body",
}


def rename_options(
    options: Mapping[str, Any], names: Mapping[str, str] = EXTRAS
) -> dict[str, Any]:
    return {names.get(key, key): value for key, value in options.items()}


def checked(adapter: Any, value: Any) -> Any:
    from pydantic import ValidationError

    try:
        return adapter.validate_python(value)
    except ValidationError as error:
        raise unsendable_input(error.title, error.errors(include_url=False)) from error


@functools.cache
def field_adapter(model: Any, key: str) -> Any:
    from typing import Annotated

    from pydantic import ConfigDict, TypeAdapter

    fields: Mapping[str, Any] | None = getattr(model, "model_fields", None)
    for name, info in (fields or model.__pydantic_fields__).items():
        if (info.serialization_alias or info.alias or name) != key:
            continue
        shape: Any = info.annotation
        if info.metadata:
            annotated: Any = Annotated
            parts = (shape, *info.metadata)
            shape = annotated[parts]
        try:
            return TypeAdapter(shape, config=ConfigDict(title=name))
        except Exception:
            return TypeAdapter(shape)
    raise KeyError(key)


def validate_field(model: Any, key: str, value: Any) -> Any:
    if value is MISSING or value is None:
        return value
    return checked(field_adapter(model, key), value)


@functools.cache
def input_adapter(shape: Any) -> Any:
    from pydantic import TypeAdapter

    return TypeAdapter(shape)


def validate_input(shape: Any, value: Any) -> Any:
    if value is MISSING or value is None:
        return value
    return checked(input_adapter(shape), value)


def extend_body(options: dict[str, Any]) -> dict[str, Any]:
    extra: Mapping[str, Any] | None = options.get("extra_body")
    if not extra:
        return options
    body: Any = options.get("body")
    dump: Any = getattr(body, "model_dump", None)
    if dump is not None:
        body = dump(by_alias=True, exclude_unset=True, mode="json")
    if body is not None and not isinstance(body, Mapping):
        raise TypeError(
            "`extra_body` adds fields to a body that is an object, and this call sends another kind.",
        )
    sent = {key: value for key, value in options.items() if key != "extra_body"}
    sent["body"] = {**cast(Mapping[str, Any], body or {}), **extra}
    return sent
