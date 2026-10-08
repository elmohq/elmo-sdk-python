from __future__ import annotations

import re
from typing import Any

from ..core.types import Codec, EncodedBody


def essence_of(media_type: str) -> str:
    return media_type.split(";", 1)[0].strip().lower()


def select_codec(codecs: list[Codec], media_type: str | None) -> Codec | None:
    if not media_type:
        return None
    essence = essence_of(media_type)
    names = (essence, re.sub(r"/.*\+", "/", essence))
    for codec in codecs:
        for candidate in codec.media_types:
            if essence_of(candidate) in names:
                return codec
    return None


def encode_named_body(
    codecs: list[Codec], media_type: str | None, options: dict[str, Any]
) -> EncodedBody | None:
    body = options.get("body")
    if body is None:
        return None
    codec = select_codec(codecs, media_type)
    if codec is None:
        return EncodedBody(content_type=media_type, payload=body)
    return codec.encode(body)
