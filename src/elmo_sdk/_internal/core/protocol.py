from __future__ import annotations

from typing import Any

from .types import Binding, Interaction


def only_protocol(
    protocols: dict[str, Any], interaction: Interaction
) -> tuple[Binding, Any]:
    setup = next(iter(protocols.values()))
    return setup["binding"], setup["transport"]


TRANSPORT_METHOD = {"unary": "unary"}


def transport_method(interaction: Interaction) -> str:
    return TRANSPORT_METHOD.get(interaction, interaction)
