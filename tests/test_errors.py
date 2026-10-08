from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from elmo_sdk import Elmo

from .stand_in import StandIn, result

if TYPE_CHECKING:
    from .stand_in import Clients


@pytest.mark.parametrize(
    ("status", "error"),
    [
        (400, Elmo.BadRequestError),
        (401, Elmo.AuthenticationError),
        (402, Elmo.PaymentRequiredError),
        (403, Elmo.PermissionDeniedError),
        (404, Elmo.NotFoundError),
        (409, Elmo.ConflictError),
        (422, Elmo.UnprocessableEntityError),
        (429, Elmo.RateLimitError),
        (500, Elmo.InternalServerError),
    ],
)
async def test_raises_the_class_named_for_the_status(
    clients: Clients, status: int, error: type[Exception]
) -> None:
    api = StandIn({"status": status})
    client = clients(api.answer, api_key="elmo_test", retry=False)
    with pytest.raises(error):
        await result(client.me.get())
