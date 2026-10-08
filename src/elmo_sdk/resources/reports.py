from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING
from uuid import UUID

from .._internal.core.missing import MISSING
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
from .._internal.page.page import async_pages, pages
from ..client import async_client, client
from .shared.auth import API_KEY_REQUIREMENTS
from .shared.request_options import AsyncRequestOptions, RequestOptions

if TYPE_CHECKING:
    from typing_extensions import Unpack

    from .._internal.core.client import AsyncClient, Client
    from .._internal.core.missing import Missing
    from .._internal.core.types import SequenceNotStr
    from .._internal.page.page import AsyncPage, Page
    from ..types.reports import CreateReportResponse, GetReportResponse, ReportSummary

LIST_REPORTS_DESCRIPTOR = OperationDescriptor(
    address="/reports",
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


CREATE_REPORT_DESCRIPTOR = OperationDescriptor(
    address="/reports",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    media_type="application/json",
    method="post",
)


GET_REPORT_DESCRIPTOR = OperationDescriptor(
    address="/reports/{reportId}",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="get",
)


class Reports:
    """Generate and retrieve AI Share of Voice reports"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def list(
        self,
        *,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> Page[ReportSummary]:
        """Retrieve a paginated list of all reports, ordered by creation date (newest
        first).

        Requires an instance admin key; organization keys receive `403`.

        Args:
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. Defaults to `20`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.reports import ReportSummary

        call_options = group_params(
            [{"in": "query", "key": "page"}, {"in": "query", "key": "limit"}],
            page=page,
            limit=limit,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return pages(
            self.client,
            LIST_REPORTS_DESCRIPTOR,
            call_options,
            ReportSummary.model_validate,
        )

    def create(
        self,
        *,
        brand_name: str,
        brand_website: str,
        brand_aliases: SequenceNotStr[str] | Missing = MISSING,
        manual_prompts: SequenceNotStr[str] | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> CreateReportResponse:
        """Create a report

        Create a new AI Share of Voice report and queue it for generation. The report
        will evaluate the brand across multiple AI engines (ChatGPT, Claude, Google AI)
        using generated and optional custom prompts.

        Requires an instance admin key; organization keys receive `403`.

        Args:
            brand_name: The brand name to analyze
            brand_website: The brand's website — a domain (nike.com) or a full URL. A URL with a path (e.g. https://www.nike.com/golf) scopes the analysis to that page; mentions are tracked against its domain either way.
            brand_aliases: Other names the brand goes by (spellings, abbreviations, product names). A mention of any of them counts as a brand mention.
            manual_prompts: Optional list of custom prompts to include in the report
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.reports import CreateReportRequest, CreateReportResponse

        call_options = group_params(
            [
                {"in": "body", "key": "brand_name", "map": "brandName"},
                {"in": "body", "key": "brand_aliases", "map": "brandAliases"},
                {"in": "body", "key": "brand_website", "map": "brandWebsite"},
                {"in": "body", "key": "manual_prompts", "map": "manualPrompts"},
            ],
            brand_name=validate_field(CreateReportRequest, "brandName", brand_name),
            brand_website=validate_field(
                CreateReportRequest, "brandWebsite", brand_website
            ),
            brand_aliases=validate_field(
                CreateReportRequest, "brandAliases", brand_aliases
            ),
            manual_prompts=manual_prompts,
        )
        call_options = extend_body(
            merge_params(
                call_options, rename_options(keyword_options(options, RequestOptions))
            ),
        )
        return send(
            self.client,
            CREATE_REPORT_DESCRIPTOR,
            call_options,
            CreateReportResponse.model_validate,
        )

    def get(
        self,
        report_id: UUID,
        *,
        k_mentions: int | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> GetReportResponse:
        """Get report status and data

        Poll a report's status. When completed, returns per-prompt snapshot data with
        raw mention counts. Consumers are responsible for computing SoV and other
        derived metrics from the raw data.

        Requires an instance admin key; organization keys receive `403`.

        Args:
            report_id: The ID of the report
            k_mentions: Number of top competitor entities to return in each prompt's mentionsTopK. Defaults to `5`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.reports import GetReportResponse

        call_options = group_params(
            [
                {"in": "path", "key": "report_id", "map": "reportId"},
                {"in": "query", "key": "k_mentions", "map": "kMentions"},
            ],
            report_id=report_id,
            k_mentions=k_mentions,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return send(
            self.client,
            GET_REPORT_DESCRIPTOR,
            call_options,
            GetReportResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> ReportsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return ReportsWithResponse(self)


class ReportsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, reports: Reports) -> None:
        self._client = reports.client
        self.create = with_response(reports.create)
        self.get = with_response(reports.get)


class AsyncReports:
    """Generate and retrieve AI Share of Voice reports"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def list(
        self,
        *,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> AsyncPage[ReportSummary]:
        """Retrieve a paginated list of all reports, ordered by creation date (newest
        first).

        Requires an instance admin key; organization keys receive `403`.

        Args:
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. Defaults to `20`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.reports import ReportSummary

        call_options = group_params(
            [{"in": "query", "key": "page"}, {"in": "query", "key": "limit"}],
            page=page,
            limit=limit,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_pages(
            self.client,
            LIST_REPORTS_DESCRIPTOR,
            call_options,
            ReportSummary.model_validate,
        )

    async def create(
        self,
        *,
        brand_name: str,
        brand_website: str,
        brand_aliases: SequenceNotStr[str] | Missing = MISSING,
        manual_prompts: SequenceNotStr[str] | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> CreateReportResponse:
        """Create a report

        Create a new AI Share of Voice report and queue it for generation. The report
        will evaluate the brand across multiple AI engines (ChatGPT, Claude, Google AI)
        using generated and optional custom prompts.

        Requires an instance admin key; organization keys receive `403`.

        Args:
            brand_name: The brand name to analyze
            brand_website: The brand's website — a domain (nike.com) or a full URL. A URL with a path (e.g. https://www.nike.com/golf) scopes the analysis to that page; mentions are tracked against its domain either way.
            brand_aliases: Other names the brand goes by (spellings, abbreviations, product names). A mention of any of them counts as a brand mention.
            manual_prompts: Optional list of custom prompts to include in the report
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.reports import CreateReportRequest, CreateReportResponse

        call_options = group_params(
            [
                {"in": "body", "key": "brand_name", "map": "brandName"},
                {"in": "body", "key": "brand_aliases", "map": "brandAliases"},
                {"in": "body", "key": "brand_website", "map": "brandWebsite"},
                {"in": "body", "key": "manual_prompts", "map": "manualPrompts"},
            ],
            brand_name=validate_field(CreateReportRequest, "brandName", brand_name),
            brand_website=validate_field(
                CreateReportRequest, "brandWebsite", brand_website
            ),
            brand_aliases=validate_field(
                CreateReportRequest, "brandAliases", brand_aliases
            ),
            manual_prompts=manual_prompts,
        )
        call_options = extend_body(
            merge_params(
                call_options,
                rename_options(keyword_options(options, AsyncRequestOptions)),
            ),
        )
        return await async_send(
            self.client,
            CREATE_REPORT_DESCRIPTOR,
            call_options,
            CreateReportResponse.model_validate,
        )

    async def get(
        self,
        report_id: UUID,
        *,
        k_mentions: int | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> GetReportResponse:
        """Get report status and data

        Poll a report's status. When completed, returns per-prompt snapshot data with
        raw mention counts. Consumers are responsible for computing SoV and other
        derived metrics from the raw data.

        Requires an instance admin key; organization keys receive `403`.

        Args:
            report_id: The ID of the report
            k_mentions: Number of top competitor entities to return in each prompt's mentionsTopK. Defaults to `5`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.reports import GetReportResponse

        call_options = group_params(
            [
                {"in": "path", "key": "report_id", "map": "reportId"},
                {"in": "query", "key": "k_mentions", "map": "kMentions"},
            ],
            report_id=report_id,
            k_mentions=k_mentions,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_send(
            self.client,
            GET_REPORT_DESCRIPTOR,
            call_options,
            GetReportResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> AsyncReportsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AsyncReportsWithResponse(self)


class AsyncReportsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, reports: AsyncReports) -> None:
        self._client = reports.client
        self.create = async_with_response(reports.create)
        self.get = async_with_response(reports.get)
