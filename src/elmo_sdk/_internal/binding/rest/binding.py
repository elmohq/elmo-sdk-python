from __future__ import annotations

import codecs
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ...codec.registry import essence_of
from ...core.config import base_url_of
from ...core.errors import ElmoError
from ...core.types import (
    Credential,
    OperationDescriptor,
    PreparedRequest,
    RawResponse,
    Result,
)
from .errors import to_api_error, unreadable_body
from .url import BuildURL

DEFAULT_ACCEPT = "application/json"


def place_in_header(credential: Credential, request: PreparedRequest) -> None:
    request.meta[credential.name.lower()] = credential.value


Placer = Callable[[Credential, PreparedRequest], None]


PLACERS: dict[str, Placer] = {"header": place_in_header}


def parser_for(content_type: str) -> str:
    if not content_type:
        return "text"
    essence = essence_of(content_type)
    if essence == "application/json" or essence.endswith("+json"):
        return "json"
    if essence.startswith("text/"):
        return "text"
    return "bytes"


def asks_for_json(request: PreparedRequest) -> bool:
    accept = request.meta.get("accept", "")
    return accept != "" and all(parser_for(one) == "json" for one in accept.split(","))


def json_or_text(text: str) -> Any:
    try:
        return json.loads(text)
    except ValueError:
        return text


WINDOWS_1252 = ("ascii", "iso8859-1")


def charset_of(content_type: str) -> str | None:
    for param in content_type.split(";")[1:]:
        name, _, value = param.partition("=")
        if name.strip().lower() == "charset":
            return value.strip().strip('"')
    return None


def read_text(raw: RawResponse, json_body: bool, ok: bool) -> str:
    label = None if json_body else charset_of(raw.headers.get("content-type", ""))
    try:
        name = codecs.lookup(label or "utf-8").name
    except LookupError:
        name = "utf-8"
    if name in WINDOWS_1252:
        name = "cp1252"
    elif name == "utf-8":
        name = "utf-8-sig"
    try:
        return raw.content.decode(name, "strict" if ok else "replace")
    except UnicodeDecodeError as cause:
        raise unreadable_body(raw, cause) from cause


@dataclass
class RestBinding:
    build_url: BuildURL
    accept: str | None = DEFAULT_ACCEPT
    name: str = "rest"

    def apply_auth(self, credential: Credential, request: PreparedRequest) -> None:
        place = PLACERS.get(credential.location)
        if place is None:
            where = credential.location
            address = request.operation.address
            raise ElmoError(
                f'This client places no credential in the {where}, so "{address}" cannot be authenticated.',
            )
        place(credential, request)

    def read_error(
        self, result: Result, request: PreparedRequest
    ) -> BaseException | None:
        response = result.response
        if (
            response is None
            or 200 <= response.status_code < 300
            and result.error is None
        ):
            return None
        return to_api_error(
            response.status_code, result.error, response, request.unauthenticated
        )

    def read_result(self, raw: RawResponse, request: PreparedRequest) -> Result:
        ok = 200 <= raw.status_code < 300
        if raw.status_code in (204, 205):
            return Result(response=raw) if ok else Result(error=None, response=raw)
        parser = parser_for(raw.headers.get("content-type", ""))
        if parser == "bytes":
            value: Any = raw.content
        else:
            text = read_text(raw, parser == "json", ok)
            if text == "":
                value = None
            elif parser == "json":
                try:
                    value = json.loads(text)
                except ValueError as cause:
                    if ok:
                        raise unreadable_body(raw, cause) from cause
                    value = text
            else:
                value = json_or_text(text) if asks_for_json(request) else text
        return (
            Result(data=value, response=raw)
            if ok
            else Result(error=value, response=raw)
        )

    def resolve_address(
        self, operation: OperationDescriptor, options: dict[str, Any]
    ) -> str:
        return self.build_url(
            address=operation.address,
            base_url=base_url_of(options, operation.base_url),
            path=options.get("path"),
            query=options.get("query"),
            serialization=operation.serialization,
        )


def create_rest_binding(build_url: BuildURL) -> RestBinding:
    return RestBinding(build_url=build_url)
