from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

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
from .._internal.core.types import OperationDescriptor
from ..client import async_client, client
from .shared.auth import API_KEY_REQUIREMENTS
from .shared.request_options import AsyncRequestOptions, RequestOptions

if TYPE_CHECKING:
    from typing_extensions import Unpack

    from .._internal.core.client import AsyncClient, Client
    from .._internal.core.missing import Missing
    from ..types.tools import AnalyzeBrandResponse

ANALYZE_BRAND_DESCRIPTOR = OperationDescriptor(
    address="/tools/analyze",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    media_type="application/json",
    method="post",
)


class Tools:
    """One-shot helpers (e.g. brand analysis) that don't persist anything"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def analyze(
        self,
        *,
        website: str,
        brand_name: str | Missing = MISSING,
        max_competitors: int | Missing = MISSING,
        max_prompts: int | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> AnalyzeBrandResponse:
        """Analyze a website

        Run brand analysis without persisting anything. Returns suggested additional
        domains, aliases, competitors, and prompts.

        Requires an instance admin key; organization keys receive `403`.

        Args:
            website: Brand's website — a hostname or a full URL. A URL with a path (e.g. https://www.nike.com/golf) is analyzed as given; the returned website is always its domain.
            brand_name: Optional brand name hint. If omitted, inferred from the domain.
            max_competitors: Maximum number of competitor suggestions. 0 disables competitor generation entirely. Defaults to `20`.
            max_prompts: Maximum number of suggested prompts. 0 disables prompt generation entirely. Defaults to `30`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.tools import AnalyzeBrandRequest, AnalyzeBrandResponse

        call_options = group_params(
            [
                {"in": "body", "key": "website"},
                {"in": "body", "key": "brand_name", "map": "brandName"},
                {"in": "body", "key": "max_competitors", "map": "maxCompetitors"},
                {"in": "body", "key": "max_prompts", "map": "maxPrompts"},
            ],
            website=validate_field(AnalyzeBrandRequest, "website", website),
            brand_name=brand_name,
            max_competitors=validate_field(
                AnalyzeBrandRequest, "maxCompetitors", max_competitors
            ),
            max_prompts=validate_field(AnalyzeBrandRequest, "maxPrompts", max_prompts),
        )
        call_options = extend_body(
            merge_params(
                call_options, rename_options(keyword_options(options, RequestOptions))
            ),
        )
        return send(
            self.client,
            ANALYZE_BRAND_DESCRIPTOR,
            call_options,
            AnalyzeBrandResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> ToolsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return ToolsWithResponse(self)


class ToolsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, tools: Tools) -> None:
        self._client = tools.client
        self.analyze = with_response(tools.analyze)


class AsyncTools:
    """One-shot helpers (e.g. brand analysis) that don't persist anything"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def analyze(
        self,
        *,
        website: str,
        brand_name: str | Missing = MISSING,
        max_competitors: int | Missing = MISSING,
        max_prompts: int | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> AnalyzeBrandResponse:
        """Analyze a website

        Run brand analysis without persisting anything. Returns suggested additional
        domains, aliases, competitors, and prompts.

        Requires an instance admin key; organization keys receive `403`.

        Args:
            website: Brand's website — a hostname or a full URL. A URL with a path (e.g. https://www.nike.com/golf) is analyzed as given; the returned website is always its domain.
            brand_name: Optional brand name hint. If omitted, inferred from the domain.
            max_competitors: Maximum number of competitor suggestions. 0 disables competitor generation entirely. Defaults to `20`.
            max_prompts: Maximum number of suggested prompts. 0 disables prompt generation entirely. Defaults to `30`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.tools import AnalyzeBrandRequest, AnalyzeBrandResponse

        call_options = group_params(
            [
                {"in": "body", "key": "website"},
                {"in": "body", "key": "brand_name", "map": "brandName"},
                {"in": "body", "key": "max_competitors", "map": "maxCompetitors"},
                {"in": "body", "key": "max_prompts", "map": "maxPrompts"},
            ],
            website=validate_field(AnalyzeBrandRequest, "website", website),
            brand_name=brand_name,
            max_competitors=validate_field(
                AnalyzeBrandRequest, "maxCompetitors", max_competitors
            ),
            max_prompts=validate_field(AnalyzeBrandRequest, "maxPrompts", max_prompts),
        )
        call_options = extend_body(
            merge_params(
                call_options,
                rename_options(keyword_options(options, AsyncRequestOptions)),
            ),
        )
        return await async_send(
            self.client,
            ANALYZE_BRAND_DESCRIPTOR,
            call_options,
            AnalyzeBrandResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> AsyncToolsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AsyncToolsWithResponse(self)


class AsyncToolsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, tools: AsyncTools) -> None:
        self._client = tools.client
        self.analyze = async_with_response(tools.analyze)
