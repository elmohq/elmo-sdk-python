from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from elmo_sdk import AsyncElmo, Elmo

from .stand_in import SUCCESS, StandIn, opened, result

if TYPE_CHECKING:
    from .stand_in import Clients


def test_builds_the_client(client: Elmo | AsyncElmo) -> None:
    assert isinstance(client, (Elmo, AsyncElmo))


async def test_sends_calls_to_the_base_url_it_was_given(clients: Clients) -> None:
    api = StandIn(SUCCESS)
    client = clients(api.answer, api_key="test", base_url="https://api.test/v1")
    await result(client.me.get())
    assert str(api.requests[0].url).startswith("https://api.test/v1/")


async def test_sends_the_headers_it_was_given_with_every_call(clients: Clients) -> None:
    api = StandIn(SUCCESS)
    client = clients(api.answer, api_key="test", default_headers={"x-test": "test"})
    await result(client.me.get())
    assert api.requests[0].headers["x-test"] == "test"


async def test_sends_no_content_type_with_a_call_that_has_no_body(
    clients: Clients,
) -> None:
    api = StandIn(SUCCESS)
    client = clients(api.answer, api_key="test")
    await result(client.me.get())
    assert "content-type" not in api.requests[0].headers


async def test_leaves_open_a_client_it_was_given(clients: Clients) -> None:
    api = StandIn(SUCCESS)
    http_client = clients.http_client(api.answer)
    async with opened(clients(api_key="test", http_client=http_client)) as client:
        await result(client.me.get())
    assert not http_client.is_closed


async def test_closes_the_client_it_opened(
    clients: Clients, monkeypatch: pytest.MonkeyPatch
) -> None:
    api = StandIn(SUCCESS)
    closed = clients.own_transport(monkeypatch, api.answer)
    async with opened(clients(api_key="test")) as client:
        await result(client.me.get())
    assert api.requests
    assert closed


async def test_sends_the_credential_in_the_authorization_header(
    clients: Clients,
) -> None:
    api = StandIn(SUCCESS)
    client = clients(api.answer, api_key="test")
    await result(client.me.get())
    assert "test" in api.requests[0].headers["authorization"]


async def test_reads_the_credential_from_elmo_api_key(
    clients: Clients, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ELMO_API_KEY", "test")
    api = StandIn(SUCCESS)
    client = clients(api.answer)
    await result(client.me.get())
    assert "test" in api.requests[0].headers["authorization"]
