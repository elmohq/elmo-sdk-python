from __future__ import annotations

from datetime import date
from functools import cached_property
from typing import TYPE_CHECKING
from uuid import UUID

from .._internal.core.missing import MISSING
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
    from .._internal.core.missing import Missing
    from ..types.snapshots import GetPromptSnapshotResponse

GET_PROMPT_SNAPSHOT_DESCRIPTOR = OperationDescriptor(
    address="/prompts/{promptId}/snapshot",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="get",
)


class Snapshot:
    """Aggregated analytics snapshots for prompts"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def get(
        self,
        prompt_id: UUID,
        *,
        start_date: date,
        end_date: date,
        k_mentions: int | Missing = MISSING,
        k_citations: int | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> GetPromptSnapshotResponse:
        """Get an aggregated snapshot of mention and citation analytics for a specific
        prompt over a date range. Use this to identify competitive gaps, track brand
        visibility trends, and discover top cited URLs.

        Args:
            prompt_id: The ID of the prompt
            start_date: Start of date range (YYYY-MM-DD)
            end_date: End of date range (YYYY-MM-DD)
            k_mentions: Number of top competitor entities to return in mentionsTopK. Defaults to `5`.
            k_citations: Number of top cited URLs to return in citedUrlsTopK. Defaults to `10`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.snapshots import GetPromptSnapshotResponse

        call_options = group_params(
            [
                {"in": "path", "key": "prompt_id", "map": "promptId"},
                {"in": "query", "key": "start_date", "map": "startDate"},
                {"in": "query", "key": "end_date", "map": "endDate"},
                {"in": "query", "key": "k_mentions", "map": "kMentions"},
                {"in": "query", "key": "k_citations", "map": "kCitations"},
            ],
            prompt_id=prompt_id,
            start_date=start_date,
            end_date=end_date,
            k_mentions=k_mentions,
            k_citations=k_citations,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return send(
            self.client,
            GET_PROMPT_SNAPSHOT_DESCRIPTOR,
            call_options,
            GetPromptSnapshotResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> SnapshotWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return SnapshotWithResponse(self)


class SnapshotWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, snapshot: Snapshot) -> None:
        self._client = snapshot.client
        self.get = with_response(snapshot.get)


class AsyncSnapshot:
    """Aggregated analytics snapshots for prompts"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def get(
        self,
        prompt_id: UUID,
        *,
        start_date: date,
        end_date: date,
        k_mentions: int | Missing = MISSING,
        k_citations: int | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> GetPromptSnapshotResponse:
        """Get an aggregated snapshot of mention and citation analytics for a specific
        prompt over a date range. Use this to identify competitive gaps, track brand
        visibility trends, and discover top cited URLs.

        Args:
            prompt_id: The ID of the prompt
            start_date: Start of date range (YYYY-MM-DD)
            end_date: End of date range (YYYY-MM-DD)
            k_mentions: Number of top competitor entities to return in mentionsTopK. Defaults to `5`.
            k_citations: Number of top cited URLs to return in citedUrlsTopK. Defaults to `10`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.snapshots import GetPromptSnapshotResponse

        call_options = group_params(
            [
                {"in": "path", "key": "prompt_id", "map": "promptId"},
                {"in": "query", "key": "start_date", "map": "startDate"},
                {"in": "query", "key": "end_date", "map": "endDate"},
                {"in": "query", "key": "k_mentions", "map": "kMentions"},
                {"in": "query", "key": "k_citations", "map": "kCitations"},
            ],
            prompt_id=prompt_id,
            start_date=start_date,
            end_date=end_date,
            k_mentions=k_mentions,
            k_citations=k_citations,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_send(
            self.client,
            GET_PROMPT_SNAPSHOT_DESCRIPTOR,
            call_options,
            GetPromptSnapshotResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> AsyncSnapshotWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AsyncSnapshotWithResponse(self)


class AsyncSnapshotWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, snapshot: AsyncSnapshot) -> None:
        self._client = snapshot.client
        self.get = async_with_response(snapshot.get)
