from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from elmo_sdk import Elmo

from .stand_in import StandIn, result, unanswered

if TYPE_CHECKING:
    from .stand_in import Clients


async def test_raises_when_the_api_does_not_answer_in_time(clients: Clients) -> None:
    client = clients(unanswered, api_key="test", retry=False)
    with pytest.raises(Elmo.TransportTimeoutError):
        await result(client.me.get())


async def test_raises_a_timeout_when_its_reply_stops_arriving(clients: Clients) -> None:
    api = StandIn({"cut": "stalled", "status": 200})
    client = clients(api.answer, api_key="test", retry=False)
    with pytest.raises(Elmo.TransportTimeoutError):
        await result(client.me.get())
    assert len(api.requests) == 1
