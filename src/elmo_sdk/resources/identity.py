from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from .._internal.core.params import keyword_options, merge_params, rename_options
from .._internal.core.response import (
    async_send,
    async_with_response,
    send,
    with_response,
)
from .._internal.core.types import OperationDescriptor
from ..client import async_client, client
from .shared.auth import API_KEY_REQUIREMENTS
from .shared.request_options import AsyncRequestOptions, RequestOptions

if TYPE_CHECKING:
    from typing_extensions import Unpack

    from .._internal.core.client import AsyncClient, Client
    from ..types.identity import GetMeResponse

GET_ME_DESCRIPTOR = OperationDescriptor(
    address="/me", auth=API_KEY_REQUIREMENTS, interaction="unary", method="get"
)


class Me:
    """What the calling key is and what it may reach"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def get(self, **options: Unpack[RequestOptions]) -> GetMeResponse:
        """Describe the calling key

        What this key is, which organization and brands it reaches, and which scopes it
        holds. Requires no scope, so it is always safe to call first when wiring up an
        integration.

        Args:
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.identity import GetMeResponse

        return send(
            self.client,
            GET_ME_DESCRIPTOR,
            merge_params({}, rename_options(keyword_options(options, RequestOptions))),
            GetMeResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> MeWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return MeWithResponse(self)


class MeWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, me: Me) -> None:
        self._client = me.client
        self.get = with_response(me.get)


class AsyncMe:
    """What the calling key is and what it may reach"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def get(self, **options: Unpack[AsyncRequestOptions]) -> GetMeResponse:
        """Describe the calling key

        What this key is, which organization and brands it reaches, and which scopes it
        holds. Requires no scope, so it is always safe to call first when wiring up an
        integration.

        Args:
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.identity import GetMeResponse

        return await async_send(
            self.client,
            GET_ME_DESCRIPTOR,
            merge_params(
                {}, rename_options(keyword_options(options, AsyncRequestOptions))
            ),
            GetMeResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> AsyncMeWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AsyncMeWithResponse(self)


class AsyncMeWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, me: AsyncMe) -> None:
        self._client = me.client
        self.get = async_with_response(me.get)
