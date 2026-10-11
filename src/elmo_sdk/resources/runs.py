from __future__ import annotations

from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING
from uuid import UUID

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
    from ..types.runs import GetRunResponse, RunSummary

LIST_PROMPT_RUNS_DESCRIPTOR = OperationDescriptor(
    address="/prompts/{promptId}/runs",
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


GET_RUN_DESCRIPTOR = OperationDescriptor(
    address="/prompts/{promptId}/runs/{runId}",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="get",
)


class Runs:
    """Individual model answers behind the aggregates"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def list(
        self,
        prompt_id: UUID,
        *,
        start: datetime,
        end: datetime,
        model: str | Missing = MISSING,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> Page[RunSummary]:
        """List runs for a prompt

        Individual model answers behind the aggregates, newest first, without their text
        — the list stays small enough to page through. Fetch `prompts.runs.get()` for
        the answer itself.

        Args:
            start: Inclusive lower bound of the window, an ISO 8601 timestamp such as `2026-01-01T00:00:00Z`. A bare `YYYY-MM-DD` is rejected: that is `/prompts/{promptId}/snapshot`'s spelling and means a local calendar day there.
            end: Exclusive upper bound of the window, an ISO 8601 timestamp. The window is half-open: a run at exactly `end` is outside it.
            model: Restrict to one model, e.g. `chatgpt`. See `models.list()`.
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. Defaults to `20`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.runs import RunSummary

        call_options = group_params(
            [
                {"in": "path", "key": "prompt_id", "map": "promptId"},
                {"in": "query", "key": "start"},
                {"in": "query", "key": "end"},
                {"in": "query", "key": "model"},
                {"in": "query", "key": "page"},
                {"in": "query", "key": "limit"},
            ],
            prompt_id=prompt_id,
            start=start,
            end=end,
            model=model,
            page=page,
            limit=limit,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return pages(
            self.client,
            LIST_PROMPT_RUNS_DESCRIPTOR,
            call_options,
            RunSummary.model_validate,
        )

    def get(
        self, prompt_id: UUID, run_id: UUID, **options: Unpack[RequestOptions]
    ) -> GetRunResponse:
        """Get a run

        One model answer, with its text normalized out of the provider’s response and
        its citations in the order the engine listed them. A run belonging to some other
        prompt answers `404`. The provider’s raw payload is deliberately not exposed —
        its shape belongs to the provider, not to this API.

        Args:
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.runs import GetRunResponse

        call_options = group_params(
            [
                {"in": "path", "key": "prompt_id", "map": "promptId"},
                {"in": "path", "key": "run_id", "map": "runId"},
            ],
            prompt_id=prompt_id,
            run_id=run_id,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return send(
            self.client, GET_RUN_DESCRIPTOR, call_options, GetRunResponse.model_validate
        )

    @cached_property
    def with_response(self) -> RunsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return RunsWithResponse(self)


class RunsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, runs: Runs) -> None:
        self._client = runs.client
        self.get = with_response(runs.get)


class AsyncRuns:
    """Individual model answers behind the aggregates"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def list(
        self,
        prompt_id: UUID,
        *,
        start: datetime,
        end: datetime,
        model: str | Missing = MISSING,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> AsyncPage[RunSummary]:
        """List runs for a prompt

        Individual model answers behind the aggregates, newest first, without their text
        — the list stays small enough to page through. Fetch `prompts.runs.get()` for
        the answer itself.

        Args:
            start: Inclusive lower bound of the window, an ISO 8601 timestamp such as `2026-01-01T00:00:00Z`. A bare `YYYY-MM-DD` is rejected: that is `/prompts/{promptId}/snapshot`'s spelling and means a local calendar day there.
            end: Exclusive upper bound of the window, an ISO 8601 timestamp. The window is half-open: a run at exactly `end` is outside it.
            model: Restrict to one model, e.g. `chatgpt`. See `models.list()`.
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. Defaults to `20`.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.runs import RunSummary

        call_options = group_params(
            [
                {"in": "path", "key": "prompt_id", "map": "promptId"},
                {"in": "query", "key": "start"},
                {"in": "query", "key": "end"},
                {"in": "query", "key": "model"},
                {"in": "query", "key": "page"},
                {"in": "query", "key": "limit"},
            ],
            prompt_id=prompt_id,
            start=start,
            end=end,
            model=model,
            page=page,
            limit=limit,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_pages(
            self.client,
            LIST_PROMPT_RUNS_DESCRIPTOR,
            call_options,
            RunSummary.model_validate,
        )

    async def get(
        self, prompt_id: UUID, run_id: UUID, **options: Unpack[AsyncRequestOptions]
    ) -> GetRunResponse:
        """Get a run

        One model answer, with its text normalized out of the provider’s response and
        its citations in the order the engine listed them. A run belonging to some other
        prompt answers `404`. The provider’s raw payload is deliberately not exposed —
        its shape belongs to the provider, not to this API.

        Args:
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.runs import GetRunResponse

        call_options = group_params(
            [
                {"in": "path", "key": "prompt_id", "map": "promptId"},
                {"in": "path", "key": "run_id", "map": "runId"},
            ],
            prompt_id=prompt_id,
            run_id=run_id,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_send(
            self.client, GET_RUN_DESCRIPTOR, call_options, GetRunResponse.model_validate
        )

    @cached_property
    def with_response(self) -> AsyncRunsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AsyncRunsWithResponse(self)


class AsyncRunsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, runs: AsyncRuns) -> None:
        self._client = runs.client
        self.get = async_with_response(runs.get)
