from __future__ import annotations

from enum import Enum
from typing import Any


class OpenEnum(Enum):
    """An enum that keeps a value it does not list.

    APIs add values over time. One this class does not list becomes a
    member of its own, whose `value` is what was sent, rather than an error.
    """

    @classmethod
    def _missing_(cls, value: object) -> Any:
        kind: Any = getattr(cls, "_member_type_", object)
        if kind is not object and isinstance(value, kind):
            member = kind.__new__(cls, value)
            member._name_ = str(value)
            member._value_ = value
            return cls._value2member_map_.setdefault(value, member)
        return None
