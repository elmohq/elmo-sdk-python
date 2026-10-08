from __future__ import annotations

import pytest

from elmo_sdk import Elmo


@pytest.mark.live
def test_answers_a_call_on_the_live_api() -> None:
    with Elmo() as client:
        response = client.with_response.me.get()
    assert response.status == 200
