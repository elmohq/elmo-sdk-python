from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

from .stand_in import SUCCESS, StandIn, result

if TYPE_CHECKING:
    from .stand_in import Clients


async def test_logs_nothing_unless_asked_to(
    clients: Clients, caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("ELMO_LOG", raising=False)
    caplog.set_level(logging.DEBUG, logger="elmo_sdk")
    api = StandIn(SUCCESS)
    client = clients(api.answer, api_key="test")
    await result(client.me.get())
    assert caplog.records == []


async def test_never_logs_the_credential(
    clients: Clients, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG, logger="elmo_sdk")
    api = StandIn(SUCCESS)
    client = clients(api.answer, api_key="test", log_level="debug")
    await result(client.me.get())
    assert caplog.records
    assert "test" not in caplog.text
