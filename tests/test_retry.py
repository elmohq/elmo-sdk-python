from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from elmo_sdk import Elmo

from .stand_in import SUCCESS, StandIn, result

if TYPE_CHECKING:
    from .stand_in import Clients


async def test_sends_a_call_again_after_429(clients: Clients) -> None:
    api = StandIn(
        {"headers": {"retry-after": "0"}, "status": 429},
        {"headers": {"retry-after": "0"}, "status": 429},
        SUCCESS,
    )
    client = clients(api.answer, api_key="elmo_test")
    await result(client.me.get())
    assert len(api.requests) == 3


async def test_sends_a_call_again_no_more_times_than_it_was_told(
    clients: Clients,
) -> None:
    api = StandIn({"headers": {"retry-after": "0"}, "status": 429})
    client = clients(api.answer, api_key="elmo_test", max_retries=1)
    with pytest.raises(Elmo.RateLimitError):
        await result(client.me.get())
    assert len(api.requests) == 2


async def test_sends_a_call_once_with_retry_off(clients: Clients) -> None:
    api = StandIn({"headers": {"retry-after": "0"}, "status": 429})
    client = clients(api.answer, api_key="elmo_test", retry=False)
    with pytest.raises(Elmo.RateLimitError):
        await result(client.me.get())
    assert len(api.requests) == 1
