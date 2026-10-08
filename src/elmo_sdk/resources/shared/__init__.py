from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .request_options import AsyncRequestOptions, RequestOptions

__all__ = ["AsyncRequestOptions", "RequestOptions"]


_LAZY_EXPORTS = {
    "AsyncRequestOptions": (".request_options", "AsyncRequestOptions"),
    "RequestOptions": (".request_options", "RequestOptions"),
}


if not TYPE_CHECKING:

    def __getattr__(name: str) -> object:
        if name not in _LAZY_EXPORTS:
            raise AttributeError(f"module {__name__} has no attribute {name}")
        module, attribute = _LAZY_EXPORTS[name]
        value = getattr(import_module(module, __name__), attribute)
        globals()[name] = value
        return value


def __dir__() -> list[str]:
    return list(__all__)
