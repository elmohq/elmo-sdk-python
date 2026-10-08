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
    from ..types.prompts import (
        CreatePromptResponse,
        DeletePromptResponse,
        GetPromptResponse,
        Prompt,
        UpdatePromptResponse,
    )
    from .runs import AsyncRuns, AsyncRunsWithResponse, Runs, RunsWithResponse
    from .snapshots import (
        AsyncSnapshot,
        AsyncSnapshotWithResponse,
        Snapshot,
        SnapshotWithResponse,
    )

LIST_PROMPTS_DESCRIPTOR = OperationDescriptor(
    address="/prompts",
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


CREATE_PROMPT_DESCRIPTOR = OperationDescriptor(
    address="/prompts",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    media_type="application/json",
    method="post",
)


DELETE_PROMPT_DESCRIPTOR = OperationDescriptor(
    address="/prompts/{promptId}",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="delete",
)


GET_PROMPT_DESCRIPTOR = OperationDescriptor(
    address="/prompts/{promptId}",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="get",
)


UPDATE_PROMPT_DESCRIPTOR = OperationDescriptor(
    address="/prompts/{promptId}",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    media_type="application/json",
    method="patch",
)


class Prompts:
    """Manage brand prompts"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def list(
        self,
        *,
        brand_id: str | Missing = MISSING,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        enabled: bool | Missing = MISSING,
        tags: str | Missing = MISSING,
        q: str | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> Page[Prompt]:
        """List all prompts

        Retrieve a paginated list of all prompts across all brands

        Args:
            brand_id: Filter prompts by brand ID
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. This list had no ceiling before, so the maximum is set to bound a runaway query rather than to change what an existing caller gets back. Defaults to `20`.
            enabled: Only prompts with this tracking state.
            tags: Comma-separated tags. A prompt matches if it carries any of them.
            q: Case-insensitive substring match on prompt text.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.prompts import Prompt

        call_options = group_params(
            [
                {"in": "query", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "page"},
                {"in": "query", "key": "limit"},
                {"in": "query", "key": "enabled"},
                {"in": "query", "key": "tags"},
                {"in": "query", "key": "q"},
            ],
            brand_id=brand_id,
            page=page,
            limit=limit,
            enabled=enabled,
            tags=tags,
            q=q,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return pages(
            self.client, LIST_PROMPTS_DESCRIPTOR, call_options, Prompt.model_validate
        )

    def create(
        self,
        *,
        brand_id: str,
        value: str,
        tags: SequenceNotStr[str] | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> CreatePromptResponse:
        """Create a new prompt

        Create a new prompt for a brand. This will automatically schedule the prompt for
        execution.

        Args:
            brand_id: Brand identifier this prompt belongs to
            value: The prompt text
            tags: User-defined tags for categorizing this prompt
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.prompts import CreatePromptRequest, CreatePromptResponse

        call_options = group_params(
            [
                {"in": "body", "key": "brand_id", "map": "brandId"},
                {"in": "body", "key": "value"},
                {"in": "body", "key": "tags"},
            ],
            brand_id=brand_id,
            value=validate_field(CreatePromptRequest, "value", value),
            tags=tags,
        )
        call_options = extend_body(
            merge_params(
                call_options, rename_options(keyword_options(options, RequestOptions))
            ),
        )
        return send(
            self.client,
            CREATE_PROMPT_DESCRIPTOR,
            call_options,
            CreatePromptResponse.model_validate,
        )

    def delete(
        self, prompt_id: UUID, **options: Unpack[RequestOptions]
    ) -> DeletePromptResponse:
        """Delete a prompt

        Permanently delete a prompt and cancel all related scheduled jobs. This will
        also cascade delete all associated prompt runs.

        Requires an instance admin key; organization keys receive `403`. The dashboard
        has no delete either — stop tracking a prompt with `prompts.update()` and
        `enabled: false`, which keeps its history and frees the plan slot.

        Args:
            prompt_id: The ID of the prompt to delete
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.prompts import DeletePromptResponse

        call_options = group_params(
            [{"in": "path", "key": "prompt_id", "map": "promptId"}], prompt_id=prompt_id
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return send(
            self.client,
            DELETE_PROMPT_DESCRIPTOR,
            call_options,
            DeletePromptResponse.model_validate,
        )

    def get(
        self, prompt_id: UUID, **options: Unpack[RequestOptions]
    ) -> GetPromptResponse:
        """Get a prompt

        Retrieve a specific prompt by ID

        Args:
            prompt_id: The ID of the prompt
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.prompts import GetPromptResponse

        call_options = group_params(
            [{"in": "path", "key": "prompt_id", "map": "promptId"}], prompt_id=prompt_id
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return send(
            self.client,
            GET_PROMPT_DESCRIPTOR,
            call_options,
            GetPromptResponse.model_validate,
        )

    def update(
        self,
        prompt_id: UUID,
        *,
        value: str | Missing = MISSING,
        enabled: bool | Missing = MISSING,
        tags: SequenceNotStr[str] | Missing = MISSING,
        premium_models: SequenceNotStr[str] | Missing = MISSING,
        **options: Unpack[RequestOptions],
    ) -> UpdatePromptResponse:
        """Update a prompt

        Update a prompt's properties. Only provided fields will be updated. Toggling
        `enabled` schedules or unschedules the recurring run job.

        Args:
            prompt_id: The ID of the prompt to update
            value: The prompt text
            enabled: Whether the prompt is enabled
            tags: User-defined tags for categorizing this prompt
            premium_models: Replaces the prompt's grounded models. Checked against the organization's premium pool.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.prompts import UpdatePromptRequest, UpdatePromptResponse

        call_options = group_params(
            [
                {"in": "path", "key": "prompt_id", "map": "promptId"},
                {"in": "body", "key": "value"},
                {"in": "body", "key": "enabled"},
                {"in": "body", "key": "tags"},
                {"in": "body", "key": "premium_models", "map": "premiumModels"},
            ],
            prompt_id=prompt_id,
            value=validate_field(UpdatePromptRequest, "value", value),
            enabled=enabled,
            tags=tags,
            premium_models=premium_models,
        )
        call_options = extend_body(
            merge_params(
                call_options, rename_options(keyword_options(options, RequestOptions))
            ),
        )
        return send(
            self.client,
            UPDATE_PROMPT_DESCRIPTOR,
            call_options,
            UpdatePromptResponse.model_validate,
        )

    @cached_property
    def runs(self) -> Runs:
        """Individual model answers behind the aggregates"""

        from .runs import Runs

        return Runs(self.client)

    @cached_property
    def snapshot(self) -> Snapshot:
        """Aggregated analytics snapshots for prompts"""

        from .snapshots import Snapshot

        return Snapshot(self.client)

    @cached_property
    def with_response(self) -> PromptsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return PromptsWithResponse(self)


class PromptsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, prompts: Prompts) -> None:
        self._client = prompts.client
        self.create = with_response(prompts.create)
        self.delete = with_response(prompts.delete)
        self.get = with_response(prompts.get)
        self.update = with_response(prompts.update)

    @cached_property
    def runs(self) -> RunsWithResponse:
        from .runs import Runs, RunsWithResponse

        return RunsWithResponse(Runs(self._client))

    @cached_property
    def snapshot(self) -> SnapshotWithResponse:
        from .snapshots import Snapshot, SnapshotWithResponse

        return SnapshotWithResponse(Snapshot(self._client))


class AsyncPrompts:
    """Manage brand prompts"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def list(
        self,
        *,
        brand_id: str | Missing = MISSING,
        page: int | Missing = MISSING,
        limit: int | Missing = MISSING,
        enabled: bool | Missing = MISSING,
        tags: str | Missing = MISSING,
        q: str | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> AsyncPage[Prompt]:
        """List all prompts

        Retrieve a paginated list of all prompts across all brands

        Args:
            brand_id: Filter prompts by brand ID
            page: Page number, 1-based. Defaults to `1`.
            limit: Items per page. Values above the maximum are clamped, not rejected. This list had no ceiling before, so the maximum is set to bound a runaway query rather than to change what an existing caller gets back. Defaults to `20`.
            enabled: Only prompts with this tracking state.
            tags: Comma-separated tags. A prompt matches if it carries any of them.
            q: Case-insensitive substring match on prompt text.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.prompts import Prompt

        call_options = group_params(
            [
                {"in": "query", "key": "brand_id", "map": "brandId"},
                {"in": "query", "key": "page"},
                {"in": "query", "key": "limit"},
                {"in": "query", "key": "enabled"},
                {"in": "query", "key": "tags"},
                {"in": "query", "key": "q"},
            ],
            brand_id=brand_id,
            page=page,
            limit=limit,
            enabled=enabled,
            tags=tags,
            q=q,
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_pages(
            self.client, LIST_PROMPTS_DESCRIPTOR, call_options, Prompt.model_validate
        )

    async def create(
        self,
        *,
        brand_id: str,
        value: str,
        tags: SequenceNotStr[str] | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> CreatePromptResponse:
        """Create a new prompt

        Create a new prompt for a brand. This will automatically schedule the prompt for
        execution.

        Args:
            brand_id: Brand identifier this prompt belongs to
            value: The prompt text
            tags: User-defined tags for categorizing this prompt
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.prompts import CreatePromptRequest, CreatePromptResponse

        call_options = group_params(
            [
                {"in": "body", "key": "brand_id", "map": "brandId"},
                {"in": "body", "key": "value"},
                {"in": "body", "key": "tags"},
            ],
            brand_id=brand_id,
            value=validate_field(CreatePromptRequest, "value", value),
            tags=tags,
        )
        call_options = extend_body(
            merge_params(
                call_options,
                rename_options(keyword_options(options, AsyncRequestOptions)),
            ),
        )
        return await async_send(
            self.client,
            CREATE_PROMPT_DESCRIPTOR,
            call_options,
            CreatePromptResponse.model_validate,
        )

    async def delete(
        self, prompt_id: UUID, **options: Unpack[AsyncRequestOptions]
    ) -> DeletePromptResponse:
        """Delete a prompt

        Permanently delete a prompt and cancel all related scheduled jobs. This will
        also cascade delete all associated prompt runs.

        Requires an instance admin key; organization keys receive `403`. The dashboard
        has no delete either — stop tracking a prompt with `prompts.update()` and
        `enabled: false`, which keeps its history and frees the plan slot.

        Args:
            prompt_id: The ID of the prompt to delete
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.prompts import DeletePromptResponse

        call_options = group_params(
            [{"in": "path", "key": "prompt_id", "map": "promptId"}], prompt_id=prompt_id
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_send(
            self.client,
            DELETE_PROMPT_DESCRIPTOR,
            call_options,
            DeletePromptResponse.model_validate,
        )

    async def get(
        self, prompt_id: UUID, **options: Unpack[AsyncRequestOptions]
    ) -> GetPromptResponse:
        """Get a prompt

        Retrieve a specific prompt by ID

        Args:
            prompt_id: The ID of the prompt
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.prompts import GetPromptResponse

        call_options = group_params(
            [{"in": "path", "key": "prompt_id", "map": "promptId"}], prompt_id=prompt_id
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_send(
            self.client,
            GET_PROMPT_DESCRIPTOR,
            call_options,
            GetPromptResponse.model_validate,
        )

    async def update(
        self,
        prompt_id: UUID,
        *,
        value: str | Missing = MISSING,
        enabled: bool | Missing = MISSING,
        tags: SequenceNotStr[str] | Missing = MISSING,
        premium_models: SequenceNotStr[str] | Missing = MISSING,
        **options: Unpack[AsyncRequestOptions],
    ) -> UpdatePromptResponse:
        """Update a prompt

        Update a prompt's properties. Only provided fields will be updated. Toggling
        `enabled` schedules or unschedules the recurring run job.

        Args:
            prompt_id: The ID of the prompt to update
            value: The prompt text
            enabled: Whether the prompt is enabled
            tags: User-defined tags for categorizing this prompt
            premium_models: Replaces the prompt's grounded models. Checked against the organization's premium pool.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.prompts import UpdatePromptRequest, UpdatePromptResponse

        call_options = group_params(
            [
                {"in": "path", "key": "prompt_id", "map": "promptId"},
                {"in": "body", "key": "value"},
                {"in": "body", "key": "enabled"},
                {"in": "body", "key": "tags"},
                {"in": "body", "key": "premium_models", "map": "premiumModels"},
            ],
            prompt_id=prompt_id,
            value=validate_field(UpdatePromptRequest, "value", value),
            enabled=enabled,
            tags=tags,
            premium_models=premium_models,
        )
        call_options = extend_body(
            merge_params(
                call_options,
                rename_options(keyword_options(options, AsyncRequestOptions)),
            ),
        )
        return await async_send(
            self.client,
            UPDATE_PROMPT_DESCRIPTOR,
            call_options,
            UpdatePromptResponse.model_validate,
        )

    @cached_property
    def runs(self) -> AsyncRuns:
        """Individual model answers behind the aggregates"""

        from .runs import AsyncRuns

        return AsyncRuns(self.client)

    @cached_property
    def snapshot(self) -> AsyncSnapshot:
        """Aggregated analytics snapshots for prompts"""

        from .snapshots import AsyncSnapshot

        return AsyncSnapshot(self.client)

    @cached_property
    def with_response(self) -> AsyncPromptsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AsyncPromptsWithResponse(self)


class AsyncPromptsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, prompts: AsyncPrompts) -> None:
        self._client = prompts.client
        self.create = async_with_response(prompts.create)
        self.delete = async_with_response(prompts.delete)
        self.get = async_with_response(prompts.get)
        self.update = async_with_response(prompts.update)

    @cached_property
    def runs(self) -> AsyncRunsWithResponse:
        from .runs import AsyncRuns, AsyncRunsWithResponse

        return AsyncRunsWithResponse(AsyncRuns(self._client))

    @cached_property
    def snapshot(self) -> AsyncSnapshotWithResponse:
        from .snapshots import AsyncSnapshot, AsyncSnapshotWithResponse

        return AsyncSnapshotWithResponse(AsyncSnapshot(self._client))
