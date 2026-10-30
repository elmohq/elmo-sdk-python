from __future__ import annotations

from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING

from .._internal.core.missing import MISSING
from .._internal.core.page import async_pages, pages
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
from .._internal.core.types import OperationDescriptor, PaginationDescriptor
from ..client import async_client, client
from .shared.auth import API_KEY_REQUIREMENTS
from .shared.request_options import AsyncRequestOptions, RequestOptions

if TYPE_CHECKING:
    from typing_extensions import Unpack

    from .._internal.core.client import AsyncClient, Client
    from .._internal.core.missing import Missing
    from .._internal.core.page import AsyncPage, Page
    from ..types.analytics import (
        CitationDomain,
        CitationURL,
        FanoutQuery,
        GetBrandAnalyticsResponse,
        ListBrandPromptPerformanceResponse,
    )

GET_BRAND_ANALYTICS_DESCRIPTOR = OperationDescriptor(
    address="/brands/{brandId}/analytics",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="get",
)


LIST_BRAND_CITATION_DOMAINS_DESCRIPTOR = OperationDescriptor(
    address="/brands/{brandId}/citations/domains",
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


LIST_BRAND_CITATION_URLS_DESCRIPTOR = OperationDescriptor(
    address="/brands/{brandId}/citations/urls",
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


LIST_BRAND_PROMPT_PERFORMANCE_DESCRIPTOR = OperationDescriptor(
    address="/brands/{brandId}/prompt-performance",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="get",
)


GET_BRAND_QUERY_FANOUT_DESCRIPTOR = OperationDescriptor(
    address="/brands/{brandId}/query-fanout",
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


class Analytics:
    """Aggregated visibility, share of voice, citations, and query fan-out for a
    brand"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def get(
        self,
        brand_id: str,
        *,
        start: datetime,
        end: datetime,
        model: str | Missing = MISSING,
        tags: str | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> GetBrandAnalyticsResponse:
        """Get a brand's analytics

        Visibility, share of voice, the per-model breakdown and the citation totals for
        one window, in one request.

        The long lists — cited domains and URLs, sub-queries, per-prompt results — are
        endpoints of their own. Everything else is always included.

        Args:
            brand_id: Brand identifier.
            start: Inclusive lower bound of the window, an ISO 8601 timestamp such as `2026-01-01T00:00:00Z`. Aligned down to the quarter hour, the grain analytics are aggregated at; where a response repeats the window, it repeats the aligned one. A bare `YYYY-MM-DD` is rejected: that is `/prompts/{promptId}/snapshot`'s spelling and means a local calendar day there.
            end: Exclusive upper bound of the window, an ISO 8601 timestamp, also aligned down to the quarter hour. The window is half-open: a run at exactly `end` is outside it. `start` and `end` inside one quarter-hour bucket leave an empty window and are rejected.
            model: Restrict to one model, e.g. `chatgpt`. See `models.list()`.
            tags: Comma-separated prompt tags. Only prompts carrying at least one of them are counted.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.analytics import GetBrandAnalyticsResponse

        call_options = group_params(
            [
                {"in": "path", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "start"},
                {"in": "query", "key": "end"},
                {"in": "query", "key": "model"},
                {"in": "query", "key": "tags"},
            ],
            brand_id=brand_id,
            start=start,
            end=end,
            model=model,
            tags=tags,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return send(
            self.client,
            GET_BRAND_ANALYTICS_DESCRIPTOR,
            call_options,
            GetBrandAnalyticsResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> AnalyticsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AnalyticsWithResponse(self)


class AnalyticsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, analytics: Analytics) -> None:
        self._client = analytics.client
        self.get = with_response(analytics.get)


class Domains:
    """Aggregated visibility, share of voice, citations, and query fan-out for a
    brand"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def list(
        self,
        brand_id: str,
        *,
        start: datetime,
        end: datetime,
        model: str | Missing = MISSING,
        tags: str | Missing = MISSING,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        q: str | Missing = MISSING,
        category: str | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> Page[CitationDomain]:
        """List cited domains

        Domains the engines cited when answering this brand's prompts, categorized and
        compared against the equal-length window immediately before this one.

        Args:
            brand_id: Brand identifier.
            start: Inclusive lower bound of the window, an ISO 8601 timestamp such as `2026-01-01T00:00:00Z`. Aligned down to the quarter hour, the grain analytics are aggregated at; where a response repeats the window, it repeats the aligned one. A bare `YYYY-MM-DD` is rejected: that is `/prompts/{promptId}/snapshot`'s spelling and means a local calendar day there.
            end: Exclusive upper bound of the window, an ISO 8601 timestamp, also aligned down to the quarter hour. The window is half-open: a run at exactly `end` is outside it. `start` and `end` inside one quarter-hour bucket leave an empty window and are rejected.
            model: Restrict to one model, e.g. `chatgpt`. See `models.list()`.
            tags: Comma-separated prompt tags. Only prompts carrying at least one of them are counted.
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. The default is large enough that most windows fit on the first page. Defaults to `1000`.
            q: Case-insensitive substring match on the domain, across every domain cited in the window.
            category: Only rows in this category, as the dashboard classifies them for this brand: `brand`, `competitor`, `editorial`, `reviews`, `ecommerce`, `social`, `developer`, `pr`, `reference`, `institutional` or `other`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.analytics import CitationDomain

        call_options = group_params(
            [
                {"in": "path", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "start"},
                {"in": "query", "key": "end"},
                {"in": "query", "key": "model"},
                {"in": "query", "key": "tags"},
                {"in": "query", "key": "page"},
                {"in": "query", "key": "limit"},
                {"in": "query", "key": "q"},
                {"in": "query", "key": "category"},
            ],
            brand_id=brand_id,
            start=start,
            end=end,
            model=model,
            tags=tags,
            page=page,
            limit=limit,
            q=q,
            category=category,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return pages(
            self.client,
            LIST_BRAND_CITATION_DOMAINS_DESCRIPTOR,
            call_options,
            CitationDomain.model_validate,
        )


class URLs:
    """Aggregated visibility, share of voice, citations, and query fan-out for a
    brand"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def list(
        self,
        brand_id: str,
        *,
        start: datetime,
        end: datetime,
        model: str | Missing = MISSING,
        tags: str | Missing = MISSING,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        q: str | Missing = MISSING,
        category: str | Missing = MISSING,
        page_type: str | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> Page[CitationURL]:
        """List cited URLs

        Individual pages the engines cited, with their category and page type.

        Args:
            brand_id: Brand identifier.
            start: Inclusive lower bound of the window, an ISO 8601 timestamp such as `2026-01-01T00:00:00Z`. Aligned down to the quarter hour, the grain analytics are aggregated at; where a response repeats the window, it repeats the aligned one. A bare `YYYY-MM-DD` is rejected: that is `/prompts/{promptId}/snapshot`'s spelling and means a local calendar day there.
            end: Exclusive upper bound of the window, an ISO 8601 timestamp, also aligned down to the quarter hour. The window is half-open: a run at exactly `end` is outside it. `start` and `end` inside one quarter-hour bucket leave an empty window and are rejected.
            model: Restrict to one model, e.g. `chatgpt`. See `models.list()`.
            tags: Comma-separated prompt tags. Only prompts carrying at least one of them are counted.
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. The default is large enough that most windows fit on the first page. Defaults to `1000`.
            q: Case-insensitive substring match on the URL or page title, across every URL cited in the window.
            category: Only rows in this category, as the dashboard classifies them for this brand: `brand`, `competitor`, `editorial`, `reviews`, `ecommerce`, `social`, `developer`, `pr`, `reference`, `institutional` or `other`.
            page_type: Only pages of this type, e.g. `article`, `review` or `product`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.analytics import CitationURL

        call_options = group_params(
            [
                {"in": "path", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "start"},
                {"in": "query", "key": "end"},
                {"in": "query", "key": "model"},
                {"in": "query", "key": "tags"},
                {"in": "query", "key": "page"},
                {"in": "query", "key": "limit"},
                {"in": "query", "key": "q"},
                {"in": "query", "key": "category"},
                {"in": "query", "key": "page_type", "map": "pageType"},
            ],
            brand_id=brand_id,
            start=start,
            end=end,
            model=model,
            tags=tags,
            page=page,
            limit=limit,
            q=q,
            category=category,
            page_type=page_type,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return pages(
            self.client,
            LIST_BRAND_CITATION_URLS_DESCRIPTOR,
            call_options,
            CitationURL.model_validate,
        )


class Citations:
    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    @cached_property
    def domains(self) -> Domains:
        """Aggregated visibility, share of voice, citations, and query fan-out for a
        brand"""

        return Domains(self.client)

    @cached_property
    def urls(self) -> URLs:
        """Aggregated visibility, share of voice, citations, and query fan-out for a
        brand"""

        return URLs(self.client)


class PromptPerformance:
    """Aggregated visibility, share of voice, citations, and query fan-out for a
    brand"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def list(
        self,
        brand_id: str,
        *,
        start: datetime,
        end: datetime,
        model: str | Missing = MISSING,
        tags: str | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> ListBrandPromptPerformanceResponse:
        """List prompt performance

        Per-prompt mention rates over the window. The analytics counterpart to
        `GET /prompts?brandId=`, which returns prompt configuration rather than results.

        A prompt the brand stopped tracking is not sampled, so it has no results over
        the window and does not appear here.

        Args:
            brand_id: Brand identifier.
            start: Inclusive lower bound of the window, an ISO 8601 timestamp such as `2026-01-01T00:00:00Z`. Aligned down to the quarter hour, the grain analytics are aggregated at; where a response repeats the window, it repeats the aligned one. A bare `YYYY-MM-DD` is rejected: that is `/prompts/{promptId}/snapshot`'s spelling and means a local calendar day there.
            end: Exclusive upper bound of the window, an ISO 8601 timestamp, also aligned down to the quarter hour. The window is half-open: a run at exactly `end` is outside it. `start` and `end` inside one quarter-hour bucket leave an empty window and are rejected.
            model: Restrict to one model, e.g. `chatgpt`. See `models.list()`.
            tags: Comma-separated prompt tags. Only prompts carrying at least one of them are counted.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.analytics import ListBrandPromptPerformanceResponse

        call_options = group_params(
            [
                {"in": "path", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "start"},
                {"in": "query", "key": "end"},
                {"in": "query", "key": "model"},
                {"in": "query", "key": "tags"},
            ],
            brand_id=brand_id,
            start=start,
            end=end,
            model=model,
            tags=tags,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return send(
            self.client,
            LIST_BRAND_PROMPT_PERFORMANCE_DESCRIPTOR,
            call_options,
            ListBrandPromptPerformanceResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> PromptPerformanceWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return PromptPerformanceWithResponse(self)


class PromptPerformanceWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, prompt_performance: PromptPerformance) -> None:
        self._client = prompt_performance.client
        self.list = with_response(prompt_performance.list)


class QueryFanout:
    """Aggregated visibility, share of voice, citations, and query fan-out for a
    brand"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def get(
        self,
        brand_id: str,
        *,
        start: datetime,
        end: datetime,
        model: str | Missing = MISSING,
        tags: str | Missing = MISSING,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        q: str | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> Page[FanoutQuery]:
        """Get query fan-out

        The searches engines ran while answering this brand's prompts. Engines that
        don't expose their searches still contribute runs, so `coverageRate` is the
        honest denominator.

        Args:
            brand_id: Brand identifier.
            start: Inclusive lower bound of the window, an ISO 8601 timestamp such as `2026-01-01T00:00:00Z`. Aligned down to the quarter hour, the grain analytics are aggregated at; where a response repeats the window, it repeats the aligned one. A bare `YYYY-MM-DD` is rejected: that is `/prompts/{promptId}/snapshot`'s spelling and means a local calendar day there.
            end: Exclusive upper bound of the window, an ISO 8601 timestamp, also aligned down to the quarter hour. The window is half-open: a run at exactly `end` is outside it. `start` and `end` inside one quarter-hour bucket leave an empty window and are rejected.
            model: Restrict to one model, e.g. `chatgpt`. See `models.list()`.
            tags: Comma-separated prompt tags. Only prompts carrying at least one of them are counted.
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. The default is large enough that most windows fit on the first page. Defaults to `1000`.
            q: Case-insensitive substring match on the search, across every search run in the window.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.analytics import FanoutQuery

        call_options = group_params(
            [
                {"in": "path", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "start"},
                {"in": "query", "key": "end"},
                {"in": "query", "key": "model"},
                {"in": "query", "key": "tags"},
                {"in": "query", "key": "page"},
                {"in": "query", "key": "limit"},
                {"in": "query", "key": "q"},
            ],
            brand_id=brand_id,
            start=start,
            end=end,
            model=model,
            tags=tags,
            page=page,
            limit=limit,
            q=q,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return pages(
            self.client,
            GET_BRAND_QUERY_FANOUT_DESCRIPTOR,
            call_options,
            FanoutQuery.model_validate,
        )


class AsyncAnalytics:
    """Aggregated visibility, share of voice, citations, and query fan-out for a
    brand"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def get(
        self,
        brand_id: str,
        *,
        start: datetime,
        end: datetime,
        model: str | Missing = MISSING,
        tags: str | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> GetBrandAnalyticsResponse:
        """Get a brand's analytics

        Visibility, share of voice, the per-model breakdown and the citation totals for
        one window, in one request.

        The long lists — cited domains and URLs, sub-queries, per-prompt results — are
        endpoints of their own. Everything else is always included.

        Args:
            brand_id: Brand identifier.
            start: Inclusive lower bound of the window, an ISO 8601 timestamp such as `2026-01-01T00:00:00Z`. Aligned down to the quarter hour, the grain analytics are aggregated at; where a response repeats the window, it repeats the aligned one. A bare `YYYY-MM-DD` is rejected: that is `/prompts/{promptId}/snapshot`'s spelling and means a local calendar day there.
            end: Exclusive upper bound of the window, an ISO 8601 timestamp, also aligned down to the quarter hour. The window is half-open: a run at exactly `end` is outside it. `start` and `end` inside one quarter-hour bucket leave an empty window and are rejected.
            model: Restrict to one model, e.g. `chatgpt`. See `models.list()`.
            tags: Comma-separated prompt tags. Only prompts carrying at least one of them are counted.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.analytics import GetBrandAnalyticsResponse

        call_options = group_params(
            [
                {"in": "path", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "start"},
                {"in": "query", "key": "end"},
                {"in": "query", "key": "model"},
                {"in": "query", "key": "tags"},
            ],
            brand_id=brand_id,
            start=start,
            end=end,
            model=model,
            tags=tags,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_send(
            self.client,
            GET_BRAND_ANALYTICS_DESCRIPTOR,
            call_options,
            GetBrandAnalyticsResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> AsyncAnalyticsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AsyncAnalyticsWithResponse(self)


class AsyncAnalyticsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, analytics: AsyncAnalytics) -> None:
        self._client = analytics.client
        self.get = async_with_response(analytics.get)


class AsyncDomains:
    """Aggregated visibility, share of voice, citations, and query fan-out for a
    brand"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def list(
        self,
        brand_id: str,
        *,
        start: datetime,
        end: datetime,
        model: str | Missing = MISSING,
        tags: str | Missing = MISSING,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        q: str | Missing = MISSING,
        category: str | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> AsyncPage[CitationDomain]:
        """List cited domains

        Domains the engines cited when answering this brand's prompts, categorized and
        compared against the equal-length window immediately before this one.

        Args:
            brand_id: Brand identifier.
            start: Inclusive lower bound of the window, an ISO 8601 timestamp such as `2026-01-01T00:00:00Z`. Aligned down to the quarter hour, the grain analytics are aggregated at; where a response repeats the window, it repeats the aligned one. A bare `YYYY-MM-DD` is rejected: that is `/prompts/{promptId}/snapshot`'s spelling and means a local calendar day there.
            end: Exclusive upper bound of the window, an ISO 8601 timestamp, also aligned down to the quarter hour. The window is half-open: a run at exactly `end` is outside it. `start` and `end` inside one quarter-hour bucket leave an empty window and are rejected.
            model: Restrict to one model, e.g. `chatgpt`. See `models.list()`.
            tags: Comma-separated prompt tags. Only prompts carrying at least one of them are counted.
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. The default is large enough that most windows fit on the first page. Defaults to `1000`.
            q: Case-insensitive substring match on the domain, across every domain cited in the window.
            category: Only rows in this category, as the dashboard classifies them for this brand: `brand`, `competitor`, `editorial`, `reviews`, `ecommerce`, `social`, `developer`, `pr`, `reference`, `institutional` or `other`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.analytics import CitationDomain

        call_options = group_params(
            [
                {"in": "path", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "start"},
                {"in": "query", "key": "end"},
                {"in": "query", "key": "model"},
                {"in": "query", "key": "tags"},
                {"in": "query", "key": "page"},
                {"in": "query", "key": "limit"},
                {"in": "query", "key": "q"},
                {"in": "query", "key": "category"},
            ],
            brand_id=brand_id,
            start=start,
            end=end,
            model=model,
            tags=tags,
            page=page,
            limit=limit,
            q=q,
            category=category,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_pages(
            self.client,
            LIST_BRAND_CITATION_DOMAINS_DESCRIPTOR,
            call_options,
            CitationDomain.model_validate,
        )


class AsyncURLs:
    """Aggregated visibility, share of voice, citations, and query fan-out for a
    brand"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def list(
        self,
        brand_id: str,
        *,
        start: datetime,
        end: datetime,
        model: str | Missing = MISSING,
        tags: str | Missing = MISSING,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        q: str | Missing = MISSING,
        category: str | Missing = MISSING,
        page_type: str | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> AsyncPage[CitationURL]:
        """List cited URLs

        Individual pages the engines cited, with their category and page type.

        Args:
            brand_id: Brand identifier.
            start: Inclusive lower bound of the window, an ISO 8601 timestamp such as `2026-01-01T00:00:00Z`. Aligned down to the quarter hour, the grain analytics are aggregated at; where a response repeats the window, it repeats the aligned one. A bare `YYYY-MM-DD` is rejected: that is `/prompts/{promptId}/snapshot`'s spelling and means a local calendar day there.
            end: Exclusive upper bound of the window, an ISO 8601 timestamp, also aligned down to the quarter hour. The window is half-open: a run at exactly `end` is outside it. `start` and `end` inside one quarter-hour bucket leave an empty window and are rejected.
            model: Restrict to one model, e.g. `chatgpt`. See `models.list()`.
            tags: Comma-separated prompt tags. Only prompts carrying at least one of them are counted.
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. The default is large enough that most windows fit on the first page. Defaults to `1000`.
            q: Case-insensitive substring match on the URL or page title, across every URL cited in the window.
            category: Only rows in this category, as the dashboard classifies them for this brand: `brand`, `competitor`, `editorial`, `reviews`, `ecommerce`, `social`, `developer`, `pr`, `reference`, `institutional` or `other`.
            page_type: Only pages of this type, e.g. `article`, `review` or `product`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.analytics import CitationURL

        call_options = group_params(
            [
                {"in": "path", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "start"},
                {"in": "query", "key": "end"},
                {"in": "query", "key": "model"},
                {"in": "query", "key": "tags"},
                {"in": "query", "key": "page"},
                {"in": "query", "key": "limit"},
                {"in": "query", "key": "q"},
                {"in": "query", "key": "category"},
                {"in": "query", "key": "page_type", "map": "pageType"},
            ],
            brand_id=brand_id,
            start=start,
            end=end,
            model=model,
            tags=tags,
            page=page,
            limit=limit,
            q=q,
            category=category,
            page_type=page_type,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_pages(
            self.client,
            LIST_BRAND_CITATION_URLS_DESCRIPTOR,
            call_options,
            CitationURL.model_validate,
        )


class AsyncCitations:
    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    @cached_property
    def domains(self) -> AsyncDomains:
        """Aggregated visibility, share of voice, citations, and query fan-out for a
        brand"""

        return AsyncDomains(self.client)

    @cached_property
    def urls(self) -> AsyncURLs:
        """Aggregated visibility, share of voice, citations, and query fan-out for a
        brand"""

        return AsyncURLs(self.client)


class AsyncPromptPerformance:
    """Aggregated visibility, share of voice, citations, and query fan-out for a
    brand"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def list(
        self,
        brand_id: str,
        *,
        start: datetime,
        end: datetime,
        model: str | Missing = MISSING,
        tags: str | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> ListBrandPromptPerformanceResponse:
        """List prompt performance

        Per-prompt mention rates over the window. The analytics counterpart to
        `GET /prompts?brandId=`, which returns prompt configuration rather than results.

        A prompt the brand stopped tracking is not sampled, so it has no results over
        the window and does not appear here.

        Args:
            brand_id: Brand identifier.
            start: Inclusive lower bound of the window, an ISO 8601 timestamp such as `2026-01-01T00:00:00Z`. Aligned down to the quarter hour, the grain analytics are aggregated at; where a response repeats the window, it repeats the aligned one. A bare `YYYY-MM-DD` is rejected: that is `/prompts/{promptId}/snapshot`'s spelling and means a local calendar day there.
            end: Exclusive upper bound of the window, an ISO 8601 timestamp, also aligned down to the quarter hour. The window is half-open: a run at exactly `end` is outside it. `start` and `end` inside one quarter-hour bucket leave an empty window and are rejected.
            model: Restrict to one model, e.g. `chatgpt`. See `models.list()`.
            tags: Comma-separated prompt tags. Only prompts carrying at least one of them are counted.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.analytics import ListBrandPromptPerformanceResponse

        call_options = group_params(
            [
                {"in": "path", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "start"},
                {"in": "query", "key": "end"},
                {"in": "query", "key": "model"},
                {"in": "query", "key": "tags"},
            ],
            brand_id=brand_id,
            start=start,
            end=end,
            model=model,
            tags=tags,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_send(
            self.client,
            LIST_BRAND_PROMPT_PERFORMANCE_DESCRIPTOR,
            call_options,
            ListBrandPromptPerformanceResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> AsyncPromptPerformanceWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AsyncPromptPerformanceWithResponse(self)


class AsyncPromptPerformanceWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, prompt_performance: AsyncPromptPerformance) -> None:
        self._client = prompt_performance.client
        self.list = async_with_response(prompt_performance.list)


class AsyncQueryFanout:
    """Aggregated visibility, share of voice, citations, and query fan-out for a
    brand"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def get(
        self,
        brand_id: str,
        *,
        start: datetime,
        end: datetime,
        model: str | Missing = MISSING,
        tags: str | Missing = MISSING,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        q: str | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> AsyncPage[FanoutQuery]:
        """Get query fan-out

        The searches engines ran while answering this brand's prompts. Engines that
        don't expose their searches still contribute runs, so `coverageRate` is the
        honest denominator.

        Args:
            brand_id: Brand identifier.
            start: Inclusive lower bound of the window, an ISO 8601 timestamp such as `2026-01-01T00:00:00Z`. Aligned down to the quarter hour, the grain analytics are aggregated at; where a response repeats the window, it repeats the aligned one. A bare `YYYY-MM-DD` is rejected: that is `/prompts/{promptId}/snapshot`'s spelling and means a local calendar day there.
            end: Exclusive upper bound of the window, an ISO 8601 timestamp, also aligned down to the quarter hour. The window is half-open: a run at exactly `end` is outside it. `start` and `end` inside one quarter-hour bucket leave an empty window and are rejected.
            model: Restrict to one model, e.g. `chatgpt`. See `models.list()`.
            tags: Comma-separated prompt tags. Only prompts carrying at least one of them are counted.
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. The default is large enough that most windows fit on the first page. Defaults to `1000`.
            q: Case-insensitive substring match on the search, across every search run in the window.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.analytics import FanoutQuery

        call_options = group_params(
            [
                {"in": "path", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "start"},
                {"in": "query", "key": "end"},
                {"in": "query", "key": "model"},
                {"in": "query", "key": "tags"},
                {"in": "query", "key": "page"},
                {"in": "query", "key": "limit"},
                {"in": "query", "key": "q"},
            ],
            brand_id=brand_id,
            start=start,
            end=end,
            model=model,
            tags=tags,
            page=page,
            limit=limit,
            q=q,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_pages(
            self.client,
            GET_BRAND_QUERY_FANOUT_DESCRIPTOR,
            call_options,
            FanoutQuery.model_validate,
        )
