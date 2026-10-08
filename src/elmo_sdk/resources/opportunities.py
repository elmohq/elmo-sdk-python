from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from .._internal.core.params import (
    group_params,
    keyword_options,
    merge_params,
    rename_options,
)
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
    from ..types.opportunities import GetBrandOpportunitiesResponse

GET_BRAND_OPPORTUNITIES_DESCRIPTOR = OperationDescriptor(
    address="/brands/{brandId}/opportunities",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="get",
)


class Opportunities:
    """Where a brand could win more citations, and why"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def get(
        self, brand_id: str, **options: Unpack[RequestOptions]
    ) -> GetBrandOpportunitiesResponse:
        """Get the latest opportunities report

        **Experimental — the response shape may still change.**

        The brand's Opportunities report: a prioritized set of ways to get cited more
        often, with the tracked prompts and cited pages behind each one. The same
        analysis the dashboard shows, from the same code.

        Generation is inline and synchronous. A stored report is served while it is
        fresh and regenerated when it is not, so there is nothing to poll for and no way
        to be handed a stale one — but a request that triggers a generation waits for
        it. The freshness window bounds the cost: however many callers ask, one
        generation per brand per window. There is deliberately no `POST`, which would
        spend provider budget with nothing metering it per call.

        Experimental.

        Args:
            brand_id: Brand identifier.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.opportunities import GetBrandOpportunitiesResponse

        call_options = group_params(
            [{"in": "path", "key": "brand_id", "map": "brandId"}], brand_id=brand_id
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return send(
            self.client,
            GET_BRAND_OPPORTUNITIES_DESCRIPTOR,
            call_options,
            GetBrandOpportunitiesResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> OpportunitiesWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return OpportunitiesWithResponse(self)


class OpportunitiesWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, opportunities: Opportunities) -> None:
        self._client = opportunities.client
        self.get = with_response(opportunities.get)


class AsyncOpportunities:
    """Where a brand could win more citations, and why"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def get(
        self, brand_id: str, **options: Unpack[AsyncRequestOptions]
    ) -> GetBrandOpportunitiesResponse:
        """Get the latest opportunities report

        **Experimental — the response shape may still change.**

        The brand's Opportunities report: a prioritized set of ways to get cited more
        often, with the tracked prompts and cited pages behind each one. The same
        analysis the dashboard shows, from the same code.

        Generation is inline and synchronous. A stored report is served while it is
        fresh and regenerated when it is not, so there is nothing to poll for and no way
        to be handed a stale one — but a request that triggers a generation waits for
        it. The freshness window bounds the cost: however many callers ask, one
        generation per brand per window. There is deliberately no `POST`, which would
        spend provider budget with nothing metering it per call.

        Experimental.

        Args:
            brand_id: Brand identifier.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.opportunities import GetBrandOpportunitiesResponse

        call_options = group_params(
            [{"in": "path", "key": "brand_id", "map": "brandId"}], brand_id=brand_id
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_send(
            self.client,
            GET_BRAND_OPPORTUNITIES_DESCRIPTOR,
            call_options,
            GetBrandOpportunitiesResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> AsyncOpportunitiesWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AsyncOpportunitiesWithResponse(self)


class AsyncOpportunitiesWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, opportunities: AsyncOpportunities) -> None:
        self._client = opportunities.client
        self.get = async_with_response(opportunities.get)
