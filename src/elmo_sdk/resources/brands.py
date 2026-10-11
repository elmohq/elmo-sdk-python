from __future__ import annotations

import builtins
from collections.abc import Sequence
from functools import cached_property
from typing import TYPE_CHECKING

from .._internal.core.missing import MISSING
from .._internal.core.page import async_pages, pages
from .._internal.core.params import (
    extend_body,
    group_params,
    keyword_options,
    merge_params,
    rename_options,
    validate_field,
    validate_input,
)
from .._internal.core.response import (
    async_send,
    async_with_response,
    send,
    with_response,
)
from .._internal.core.types import OperationDescriptor, PaginationDescriptor
from ..client import async_client, client
from .shared.auth import API_KEY_REQUIREMENTS
from .shared.request_options import AsyncRequestOptions, RequestOptions

if TYPE_CHECKING:
    from typing_extensions import Unpack

    from .._internal.core.client import AsyncClient, Client
    from .._internal.core.missing import Missing
    from .._internal.core.page import AsyncPage, Page
    from .._internal.core.types import SequenceNotStr
    from ..types.brands import (
        Brand,
        CreateBrandRequestCompetitorsItem,
        CreateBrandRequestCompetitorsItemDict,
        CreateBrandRequestPromptsItem,
        CreateBrandRequestPromptsItemDict,
        CreateBrandResponse,
        GetBrandResponse,
        UpdateBrandResponse,
    )
    from .analytics import (
        Analytics,
        AnalyticsWithResponse,
        AsyncAnalytics,
        AsyncAnalyticsWithResponse,
        AsyncCitations,
        AsyncCitationsWithResponse,
        AsyncPromptPerformance,
        AsyncPromptPerformanceWithResponse,
        AsyncQueryFanout,
        AsyncQueryFanoutWithResponse,
        Citations,
        CitationsWithResponse,
        PromptPerformance,
        PromptPerformanceWithResponse,
        QueryFanout,
        QueryFanoutWithResponse,
    )
    from .opportunities import (
        AsyncOpportunities,
        AsyncOpportunitiesWithResponse,
        Opportunities,
        OpportunitiesWithResponse,
    )
    from .tags import AsyncTags, AsyncTagsWithResponse, Tags, TagsWithResponse

LIST_BRANDS_DESCRIPTOR = OperationDescriptor(
    address="/brands",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="get",
    pagination=PaginationDescriptor(
        style="page",
        items="data",
        limit_param="limit",
        pages="pagination.totalPages",
        param="page",
        size="pagination.limit",
        total="pagination.total",
    ),
)


CREATE_BRAND_DESCRIPTOR = OperationDescriptor(
    address="/brands",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    media_type="application/json",
    method="post",
)


GET_BRAND_DESCRIPTOR = OperationDescriptor(
    address="/brands/{brandId}",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="get",
)


UPDATE_BRAND_DESCRIPTOR = OperationDescriptor(
    address="/brands/{brandId}",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    media_type="application/json",
    method="patch",
)


class Brands:
    """Manage brand records"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def list(
        self,
        *,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> Page[Brand]:
        """
        Args:
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. Defaults to `20`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.brands import Brand

        call_options = group_params(
            [{"in": "query", "key": "page"}, {"in": "query", "key": "limit"}],
            page=page,
            limit=limit,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return pages(
            self.client, LIST_BRANDS_DESCRIPTOR, call_options, Brand.model_validate
        )

    def create(
        self,
        *,
        id: str,
        name: str,
        domains: SequenceNotStr[str],
        aliases: SequenceNotStr[str] | Missing = MISSING,
        competitors: Sequence[
            CreateBrandRequestCompetitorsItem | CreateBrandRequestCompetitorsItemDict
        ]
        | Missing = MISSING,
        prompts: Sequence[
            CreateBrandRequestPromptsItem | CreateBrandRequestPromptsItemDict
        ]
        | Missing = MISSING,
        organization_id: str | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> CreateBrandResponse:
        """Create a brand

        Args:
            domains: Brand domains. The first entry is the primary website; remaining entries are additional domains.
            organization_id: Organization to create the brand in. **Organization key**, Omitted: creates in the key's own organization. **Organization key**, Present: must name the key's own organization; any other value is a `400`. **Admin key**, Omitted: provisions a new organization named after the brand id. **Admin key**, Present: creates in the named organization, which must already exist — `404` if it does not. An admin key omitting this field is currently the only way to create an organization over the API.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.brands import (
            CreateBrandRequest,
            CreateBrandRequestCompetitorsItem,
            CreateBrandRequestPromptsItem,
            CreateBrandResponse,
        )

        call_options = group_params(
            [
                {"in": "body", "key": "id"},
                {"in": "body", "key": "name"},
                {"in": "body", "key": "domains"},
                {"in": "body", "key": "aliases"},
                {"in": "body", "key": "competitors"},
                {"in": "body", "key": "prompts"},
                {"in": "body", "key": "organization_id", "map": "organizationId"},
            ],
            id=validate_field(CreateBrandRequest, "id", id),
            name=validate_field(CreateBrandRequest, "name", name),
            domains=validate_field(CreateBrandRequest, "domains", domains),
            aliases=aliases,
            competitors=validate_input(
                builtins.list[CreateBrandRequestCompetitorsItem], competitors
            ),
            prompts=validate_input(
                builtins.list[CreateBrandRequestPromptsItem], prompts
            ),
            organization_id=organization_id,
        )
        call_options = extend_body(
            merge_params(
                call_options, rename_options(keyword_options(options, RequestOptions))
            ),
        )
        return send(
            self.client,
            CREATE_BRAND_DESCRIPTOR,
            call_options,
            CreateBrandResponse.model_validate,
        )

    def get(self, brand_id: str, **options: Unpack[RequestOptions]) -> GetBrandResponse:
        """Get a brand

        Args:
            brand_id: Brand identifier
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.brands import GetBrandResponse

        call_options = group_params(
            [{"in": "path", "key": "brand_id", "map": "brandId"}], brand_id=brand_id
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return send(
            self.client,
            GET_BRAND_DESCRIPTOR,
            call_options,
            GetBrandResponse.model_validate,
        )

    def update(
        self,
        brand_id: str,
        *,
        brand_name: str | Missing = MISSING,
        domains: SequenceNotStr[str] | Missing = MISSING,
        aliases: SequenceNotStr[str] | Missing = MISSING,
        enabled: bool | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> UpdateBrandResponse:
        """Update a brand

        Args:
            brand_id: Brand identifier
            domains: Brand domains. The first entry is the primary website; remaining entries are additional domains.
            enabled: Whether the brand is sampled at all. **Modifiable only with an instance admin key**: setting it with an organization key is a `403`, because disabling ends tracking silently while the plan keeps being billed and no dashboard control does it at any role.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.brands import UpdateBrandRequest, UpdateBrandResponse

        call_options = group_params(
            [
                {"in": "path", "key": "brand_id", "map": "brandId"},
                {"in": "body", "key": "brand_name", "map": "brandName"},
                {"in": "body", "key": "domains"},
                {"in": "body", "key": "aliases"},
                {"in": "body", "key": "enabled"},
            ],
            brand_id=brand_id,
            brand_name=validate_field(UpdateBrandRequest, "brandName", brand_name),
            domains=validate_field(UpdateBrandRequest, "domains", domains),
            aliases=aliases,
            enabled=enabled,
        )
        call_options = extend_body(
            merge_params(
                call_options, rename_options(keyword_options(options, RequestOptions))
            ),
        )
        return send(
            self.client,
            UPDATE_BRAND_DESCRIPTOR,
            call_options,
            UpdateBrandResponse.model_validate,
        )

    @cached_property
    def analytics(self) -> Analytics:
        """Aggregated visibility, share of voice, citations, and query fan-out for a
        brand"""

        from .analytics import Analytics

        return Analytics(self.client)

    @cached_property
    def citations(self) -> Citations:
        from .analytics import Citations

        return Citations(self.client)

    @cached_property
    def opportunities(self) -> Opportunities:
        """Where a brand could win more citations, and why"""

        from .opportunities import Opportunities

        return Opportunities(self.client)

    @cached_property
    def prompt_performance(self) -> PromptPerformance:
        """Aggregated visibility, share of voice, citations, and query fan-out for a
        brand"""

        from .analytics import PromptPerformance

        return PromptPerformance(self.client)

    @cached_property
    def query_fanout(self) -> QueryFanout:
        """Aggregated visibility, share of voice, citations, and query fan-out for a
        brand"""

        from .analytics import QueryFanout

        return QueryFanout(self.client)

    @cached_property
    def tags(self) -> Tags:
        """The tags in use on a brand's prompts"""

        from .tags import Tags

        return Tags(self.client)

    @cached_property
    def with_response(self) -> BrandsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return BrandsWithResponse(self)


class BrandsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, brands: Brands) -> None:
        self._client = brands.client
        self.create = with_response(brands.create)
        self.get = with_response(brands.get)
        self.update = with_response(brands.update)

    @cached_property
    def analytics(self) -> AnalyticsWithResponse:
        from .analytics import Analytics, AnalyticsWithResponse

        return AnalyticsWithResponse(Analytics(self._client))

    @cached_property
    def citations(self) -> CitationsWithResponse:
        from .analytics import Citations, CitationsWithResponse

        return CitationsWithResponse(Citations(self._client))

    @cached_property
    def opportunities(self) -> OpportunitiesWithResponse:
        from .opportunities import Opportunities, OpportunitiesWithResponse

        return OpportunitiesWithResponse(Opportunities(self._client))

    @cached_property
    def prompt_performance(self) -> PromptPerformanceWithResponse:
        from .analytics import PromptPerformance, PromptPerformanceWithResponse

        return PromptPerformanceWithResponse(PromptPerformance(self._client))

    @cached_property
    def query_fanout(self) -> QueryFanoutWithResponse:
        from .analytics import QueryFanout, QueryFanoutWithResponse

        return QueryFanoutWithResponse(QueryFanout(self._client))

    @cached_property
    def tags(self) -> TagsWithResponse:
        from .tags import Tags, TagsWithResponse

        return TagsWithResponse(Tags(self._client))


class AsyncBrands:
    """Manage brand records"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def list(
        self,
        *,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> AsyncPage[Brand]:
        """
        Args:
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. Defaults to `20`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.brands import Brand

        call_options = group_params(
            [{"in": "query", "key": "page"}, {"in": "query", "key": "limit"}],
            page=page,
            limit=limit,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_pages(
            self.client, LIST_BRANDS_DESCRIPTOR, call_options, Brand.model_validate
        )

    async def create(
        self,
        *,
        id: str,
        name: str,
        domains: SequenceNotStr[str],
        aliases: SequenceNotStr[str] | Missing = MISSING,
        competitors: Sequence[
            CreateBrandRequestCompetitorsItem | CreateBrandRequestCompetitorsItemDict
        ]
        | Missing = MISSING,
        prompts: Sequence[
            CreateBrandRequestPromptsItem | CreateBrandRequestPromptsItemDict
        ]
        | Missing = MISSING,
        organization_id: str | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> CreateBrandResponse:
        """Create a brand

        Args:
            domains: Brand domains. The first entry is the primary website; remaining entries are additional domains.
            organization_id: Organization to create the brand in. **Organization key**, Omitted: creates in the key's own organization. **Organization key**, Present: must name the key's own organization; any other value is a `400`. **Admin key**, Omitted: provisions a new organization named after the brand id. **Admin key**, Present: creates in the named organization, which must already exist — `404` if it does not. An admin key omitting this field is currently the only way to create an organization over the API.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.brands import (
            CreateBrandRequest,
            CreateBrandRequestCompetitorsItem,
            CreateBrandRequestPromptsItem,
            CreateBrandResponse,
        )

        call_options = group_params(
            [
                {"in": "body", "key": "id"},
                {"in": "body", "key": "name"},
                {"in": "body", "key": "domains"},
                {"in": "body", "key": "aliases"},
                {"in": "body", "key": "competitors"},
                {"in": "body", "key": "prompts"},
                {"in": "body", "key": "organization_id", "map": "organizationId"},
            ],
            id=validate_field(CreateBrandRequest, "id", id),
            name=validate_field(CreateBrandRequest, "name", name),
            domains=validate_field(CreateBrandRequest, "domains", domains),
            aliases=aliases,
            competitors=validate_input(
                builtins.list[CreateBrandRequestCompetitorsItem], competitors
            ),
            prompts=validate_input(
                builtins.list[CreateBrandRequestPromptsItem], prompts
            ),
            organization_id=organization_id,
        )
        call_options = extend_body(
            merge_params(
                call_options,
                rename_options(keyword_options(options, AsyncRequestOptions)),
            ),
        )
        return await async_send(
            self.client,
            CREATE_BRAND_DESCRIPTOR,
            call_options,
            CreateBrandResponse.model_validate,
        )

    async def get(
        self, brand_id: str, **options: Unpack[AsyncRequestOptions]
    ) -> GetBrandResponse:
        """Get a brand

        Args:
            brand_id: Brand identifier
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.brands import GetBrandResponse

        call_options = group_params(
            [{"in": "path", "key": "brand_id", "map": "brandId"}], brand_id=brand_id
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_send(
            self.client,
            GET_BRAND_DESCRIPTOR,
            call_options,
            GetBrandResponse.model_validate,
        )

    async def update(
        self,
        brand_id: str,
        *,
        brand_name: str | Missing = MISSING,
        domains: SequenceNotStr[str] | Missing = MISSING,
        aliases: SequenceNotStr[str] | Missing = MISSING,
        enabled: bool | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> UpdateBrandResponse:
        """Update a brand

        Args:
            brand_id: Brand identifier
            domains: Brand domains. The first entry is the primary website; remaining entries are additional domains.
            enabled: Whether the brand is sampled at all. **Modifiable only with an instance admin key**: setting it with an organization key is a `403`, because disabling ends tracking silently while the plan keeps being billed and no dashboard control does it at any role.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.brands import UpdateBrandRequest, UpdateBrandResponse

        call_options = group_params(
            [
                {"in": "path", "key": "brand_id", "map": "brandId"},
                {"in": "body", "key": "brand_name", "map": "brandName"},
                {"in": "body", "key": "domains"},
                {"in": "body", "key": "aliases"},
                {"in": "body", "key": "enabled"},
            ],
            brand_id=brand_id,
            brand_name=validate_field(UpdateBrandRequest, "brandName", brand_name),
            domains=validate_field(UpdateBrandRequest, "domains", domains),
            aliases=aliases,
            enabled=enabled,
        )
        call_options = extend_body(
            merge_params(
                call_options,
                rename_options(keyword_options(options, AsyncRequestOptions)),
            ),
        )
        return await async_send(
            self.client,
            UPDATE_BRAND_DESCRIPTOR,
            call_options,
            UpdateBrandResponse.model_validate,
        )

    @cached_property
    def analytics(self) -> AsyncAnalytics:
        """Aggregated visibility, share of voice, citations, and query fan-out for a
        brand"""

        from .analytics import AsyncAnalytics

        return AsyncAnalytics(self.client)

    @cached_property
    def citations(self) -> AsyncCitations:
        from .analytics import AsyncCitations

        return AsyncCitations(self.client)

    @cached_property
    def opportunities(self) -> AsyncOpportunities:
        """Where a brand could win more citations, and why"""

        from .opportunities import AsyncOpportunities

        return AsyncOpportunities(self.client)

    @cached_property
    def prompt_performance(self) -> AsyncPromptPerformance:
        """Aggregated visibility, share of voice, citations, and query fan-out for a
        brand"""

        from .analytics import AsyncPromptPerformance

        return AsyncPromptPerformance(self.client)

    @cached_property
    def query_fanout(self) -> AsyncQueryFanout:
        """Aggregated visibility, share of voice, citations, and query fan-out for a
        brand"""

        from .analytics import AsyncQueryFanout

        return AsyncQueryFanout(self.client)

    @cached_property
    def tags(self) -> AsyncTags:
        """The tags in use on a brand's prompts"""

        from .tags import AsyncTags

        return AsyncTags(self.client)

    @cached_property
    def with_response(self) -> AsyncBrandsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AsyncBrandsWithResponse(self)


class AsyncBrandsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, brands: AsyncBrands) -> None:
        self._client = brands.client
        self.create = async_with_response(brands.create)
        self.get = async_with_response(brands.get)
        self.update = async_with_response(brands.update)

    @cached_property
    def analytics(self) -> AsyncAnalyticsWithResponse:
        from .analytics import AsyncAnalytics, AsyncAnalyticsWithResponse

        return AsyncAnalyticsWithResponse(AsyncAnalytics(self._client))

    @cached_property
    def citations(self) -> AsyncCitationsWithResponse:
        from .analytics import AsyncCitations, AsyncCitationsWithResponse

        return AsyncCitationsWithResponse(AsyncCitations(self._client))

    @cached_property
    def opportunities(self) -> AsyncOpportunitiesWithResponse:
        from .opportunities import AsyncOpportunities, AsyncOpportunitiesWithResponse

        return AsyncOpportunitiesWithResponse(AsyncOpportunities(self._client))

    @cached_property
    def prompt_performance(self) -> AsyncPromptPerformanceWithResponse:
        from .analytics import (
            AsyncPromptPerformance,
            AsyncPromptPerformanceWithResponse,
        )

        return AsyncPromptPerformanceWithResponse(AsyncPromptPerformance(self._client))

    @cached_property
    def query_fanout(self) -> AsyncQueryFanoutWithResponse:
        from .analytics import AsyncQueryFanout, AsyncQueryFanoutWithResponse

        return AsyncQueryFanoutWithResponse(AsyncQueryFanout(self._client))

    @cached_property
    def tags(self) -> AsyncTagsWithResponse:
        from .tags import AsyncTags, AsyncTagsWithResponse

        return AsyncTagsWithResponse(AsyncTags(self._client))
