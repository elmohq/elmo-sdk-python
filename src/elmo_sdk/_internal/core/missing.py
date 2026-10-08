from __future__ import annotations


class Missing:
    """The type of `MISSING`, for annotating an argument that may hold it."""

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "MISSING"


MISSING: Missing = Missing()
"""What an argument holds when the caller said nothing about it.

An argument left at this default is not sent, where `None` is sent as JSON `null`.
Where an argument defaults to `None` instead, `None` sends the client's own
value and `MISSING` sends nothing.

"""
