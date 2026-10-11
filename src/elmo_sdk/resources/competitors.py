from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING
from uuid import UUID

from .._internal.core.missing import MISSING
from .._internal.core.page import async_pages, pages
from .._internal.core.params import (
    extend_body,
    group_params,
    keyword_options,
    merge_params,
    rename_options,
    validate_field,
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
    from ..types.competitors import (
        Competitor,
        CreateCompetitorResponse,
        DeleteCompetitorResponse,
        GetCompetitorResponse,
        UpdateCompetitorResponse,
    )

LIST_COMPETITORS_DESCRIPTOR = OperationDescriptor(
    address="/competitors",
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


CREATE_COMPETITOR_DESCRIPTOR = OperationDescriptor(
    address="/competitors",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    media_type="application/json",
    method="post",
)


DELETE_COMPETITOR_DESCRIPTOR = OperationDescriptor(
    address="/competitors/{competitorId}",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="delete",
)


GET_COMPETITOR_DESCRIPTOR = OperationDescriptor(
    address="/competitors/{competitorId}",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="get",
)


UPDATE_COMPETITOR_DESCRIPTOR = OperationDescriptor(
    address="/competitors/{competitorId}",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    media_type="application/json",
    method="patch",
)


class Competitors:
    """Manage brand competitors"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def list(
        self,
        *,
        brand_id: str | Missing = MISSING,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> Page[Competitor]:
        """
        Args:
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. Defaults to `20`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.competitors import Competitor

        call_options = group_params(
            [
                {"in": "query", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "page"},
                {"in": "query", "key": "limit"},
            ],
            brand_id=brand_id,
            page=page,
            limit=limit,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return pages(
            self.client,
            LIST_COMPETITORS_DESCRIPTOR,
            call_options,
            Competitor.model_validate,
        )

    def create(
        self,
        *,
        brand_id: str,
        name: str,
        domains: SequenceNotStr[str] | Missing = MISSING,
        aliases: SequenceNotStr[str] | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> CreateCompetitorResponse:
        """Add a competitor

        Args:
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.competitors import (
            CreateCompetitorRequest,
            CreateCompetitorResponse,
        )

        call_options = group_params(
            [
                {"in": "body", "key": "brand_id", "map": "brandId"},
                {"in": "body", "key": "name"},
                {"in": "body", "key": "domains"},
                {"in": "body", "key": "aliases"},
            ],
            brand_id=validate_field(CreateCompetitorRequest, "brandId", brand_id),
            name=validate_field(CreateCompetitorRequest, "name", name),
            domains=domains,
            aliases=aliases,
        )
        call_options = extend_body(
            merge_params(
                call_options, rename_options(keyword_options(options, RequestOptions))
            ),
        )
        return send(
            self.client,
            CREATE_COMPETITOR_DESCRIPTOR,
            call_options,
            CreateCompetitorResponse.model_validate,
        )

    def delete(
        self, competitor_id: UUID, **options: Unpack[RequestOptions]
    ) -> DeleteCompetitorResponse:
        """Delete a competitor

        Args:
            competitor_id: Competitor identifier (UUID)
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.competitors import DeleteCompetitorResponse

        call_options = group_params(
            [{"in": "path", "key": "competitor_id", "map": "competitorId"}],
            competitor_id=competitor_id,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return send(
            self.client,
            DELETE_COMPETITOR_DESCRIPTOR,
            call_options,
            DeleteCompetitorResponse.model_validate,
        )

    def get(
        self, competitor_id: UUID, **options: Unpack[RequestOptions]
    ) -> GetCompetitorResponse:
        """Get a competitor

        Args:
            competitor_id: Competitor identifier (UUID)
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.competitors import GetCompetitorResponse

        call_options = group_params(
            [{"in": "path", "key": "competitor_id", "map": "competitorId"}],
            competitor_id=competitor_id,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return send(
            self.client,
            GET_COMPETITOR_DESCRIPTOR,
            call_options,
            GetCompetitorResponse.model_validate,
        )

    def update(
        self,
        competitor_id: UUID,
        *,
        name: str | Missing = MISSING,
        domains: SequenceNotStr[str] | Missing = MISSING,
        aliases: SequenceNotStr[str] | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> UpdateCompetitorResponse:
        """Update a competitor

        Args:
            competitor_id: Competitor identifier (UUID)
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.competitors import (
            UpdateCompetitorRequest,
            UpdateCompetitorResponse,
        )

        call_options = group_params(
            [
                {"in": "path", "key": "competitor_id", "map": "competitorId"},
                {"in": "body", "key": "name"},
                {"in": "body", "key": "domains"},
                {"in": "body", "key": "aliases"},
            ],
            competitor_id=competitor_id,
            name=validate_field(UpdateCompetitorRequest, "name", name),
            domains=domains,
            aliases=aliases,
        )
        call_options = extend_body(
            merge_params(
                call_options, rename_options(keyword_options(options, RequestOptions))
            ),
        )
        return send(
            self.client,
            UPDATE_COMPETITOR_DESCRIPTOR,
            call_options,
            UpdateCompetitorResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> CompetitorsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return CompetitorsWithResponse(self)


class CompetitorsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, competitors: Competitors) -> None:
        self._client = competitors.client
        self.create = with_response(competitors.create)
        self.delete = with_response(competitors.delete)
        self.get = with_response(competitors.get)
        self.update = with_response(competitors.update)


class AsyncCompetitors:
    """Manage brand competitors"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def list(
        self,
        *,
        brand_id: str | Missing = MISSING,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> AsyncPage[Competitor]:
        """
        Args:
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. Defaults to `20`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.competitors import Competitor

        call_options = group_params(
            [
                {"in": "query", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "page"},
                {"in": "query", "key": "limit"},
            ],
            brand_id=brand_id,
            page=page,
            limit=limit,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_pages(
            self.client,
            LIST_COMPETITORS_DESCRIPTOR,
            call_options,
            Competitor.model_validate,
        )

    async def create(
        self,
        *,
        brand_id: str,
        name: str,
        domains: SequenceNotStr[str] | Missing = MISSING,
        aliases: SequenceNotStr[str] | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> CreateCompetitorResponse:
        """Add a competitor

        Args:
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.competitors import (
            CreateCompetitorRequest,
            CreateCompetitorResponse,
        )

        call_options = group_params(
            [
                {"in": "body", "key": "brand_id", "map": "brandId"},
                {"in": "body", "key": "name"},
                {"in": "body", "key": "domains"},
                {"in": "body", "key": "aliases"},
            ],
            brand_id=validate_field(CreateCompetitorRequest, "brandId", brand_id),
            name=validate_field(CreateCompetitorRequest, "name", name),
            domains=domains,
            aliases=aliases,
        )
        call_options = extend_body(
            merge_params(
                call_options,
                rename_options(keyword_options(options, AsyncRequestOptions)),
            ),
        )
        return await async_send(
            self.client,
            CREATE_COMPETITOR_DESCRIPTOR,
            call_options,
            CreateCompetitorResponse.model_validate,
        )

    async def delete(
        self, competitor_id: UUID, **options: Unpack[AsyncRequestOptions]
    ) -> DeleteCompetitorResponse:
        """Delete a competitor

        Args:
            competitor_id: Competitor identifier (UUID)
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.competitors import DeleteCompetitorResponse

        call_options = group_params(
            [{"in": "path", "key": "competitor_id", "map": "competitorId"}],
            competitor_id=competitor_id,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_send(
            self.client,
            DELETE_COMPETITOR_DESCRIPTOR,
            call_options,
            DeleteCompetitorResponse.model_validate,
        )

    async def get(
        self, competitor_id: UUID, **options: Unpack[AsyncRequestOptions]
    ) -> GetCompetitorResponse:
        """Get a competitor

        Args:
            competitor_id: Competitor identifier (UUID)
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.competitors import GetCompetitorResponse

        call_options = group_params(
            [{"in": "path", "key": "competitor_id", "map": "competitorId"}],
            competitor_id=competitor_id,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_send(
            self.client,
            GET_COMPETITOR_DESCRIPTOR,
            call_options,
            GetCompetitorResponse.model_validate,
        )

    async def update(
        self,
        competitor_id: UUID,
        *,
        name: str | Missing = MISSING,
        domains: SequenceNotStr[str] | Missing = MISSING,
        aliases: SequenceNotStr[str] | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> UpdateCompetitorResponse:
        """Update a competitor

        Args:
            competitor_id: Competitor identifier (UUID)
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.competitors import (
            UpdateCompetitorRequest,
            UpdateCompetitorResponse,
        )

        call_options = group_params(
            [
                {"in": "path", "key": "competitor_id", "map": "competitorId"},
                {"in": "body", "key": "name"},
                {"in": "body", "key": "domains"},
                {"in": "body", "key": "aliases"},
            ],
            competitor_id=competitor_id,
            name=validate_field(UpdateCompetitorRequest, "name", name),
            domains=domains,
            aliases=aliases,
        )
        call_options = extend_body(
            merge_params(
                call_options,
                rename_options(keyword_options(options, AsyncRequestOptions)),
            ),
        )
        return await async_send(
            self.client,
            UPDATE_COMPETITOR_DESCRIPTOR,
            call_options,
            UpdateCompetitorResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> AsyncCompetitorsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AsyncCompetitorsWithResponse(self)


class AsyncCompetitorsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, competitors: AsyncCompetitors) -> None:
        self._client = competitors.client
        self.create = async_with_response(competitors.create)
        self.delete = async_with_response(competitors.delete)
        self.get = async_with_response(competitors.get)
        self.update = async_with_response(competitors.update)
