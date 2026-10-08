from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from elmo_sdk import Elmo

from .stand_in import SUCCESS, StandIn, result

if TYPE_CHECKING:
    from .stand_in import Clients


async def test_hands_back_the_reply_with_what_it_decoded(clients: Clients) -> None:
    api = StandIn(dict(SUCCESS, headers={"x-test": "test"}))
    client = clients(api.answer, api_key="elmo_test")
    response = await result(client.with_response.me.get())
    assert response.status == 200
    assert response.response.headers["x-test"] == "test"


async def test_sends_a_call_again_when_its_reply_breaks_off(clients: Clients) -> None:
    api = StandIn({"cut": "broken", "status": 200})
    client = clients(
        api.answer, api_key="elmo_test", retry={"delay": 0, "max_retries": 1}
    )
    with pytest.raises(Elmo.TransportError):
        await result(client.me.get())
    assert len(api.requests) == 2


async def test_raises_a_decode_error_when_a_success_has_no_body(
    clients: Clients,
) -> None:
    api = StandIn({"status": 200})
    client = clients(api.answer, api_key="elmo_test")
    with pytest.raises(Elmo.DecodeError):
        await result(client.me.get())
    assert len(api.requests) == 1
