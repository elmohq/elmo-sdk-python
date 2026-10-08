from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .common import OpenEnum
    from .error import Error
    from .mention_entry import MentionEntry, MentionsSummary
    from .pagination import Pagination

__all__ = ["Error", "MentionEntry", "MentionsSummary", "OpenEnum", "Pagination"]


_LAZY_EXPORTS = {
    "Error": (".error", "Error"),
    "MentionEntry": (".mention_entry", "MentionEntry"),
    "MentionsSummary": (".mention_entry", "MentionsSummary"),
    "OpenEnum": (".common", "OpenEnum"),
    "Pagination": (".pagination", "Pagination"),
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
