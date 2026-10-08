from __future__ import annotations

import pytest

from elmo_sdk import AsyncElmo, Elmo

from .stand_in import Clients


@pytest.fixture(params=[Elmo, AsyncElmo], ids=["sync", "async"])
def client(request: pytest.FixtureRequest) -> Elmo | AsyncElmo:
    root: type[Elmo | AsyncElmo] = request.param
    return root(api_key="elmo_test")


@pytest.fixture(params=[Elmo, AsyncElmo], ids=["sync", "async"])
def clients(request: pytest.FixtureRequest) -> Clients:
    return Clients(request.param)
