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
    from ..types.tags import ListBrandTagsResponse

LIST_BRAND_TAGS_DESCRIPTOR = OperationDescriptor(
    address="/brands/{brandId}/tags",
    auth=API_KEY_REQUIREMENTS,
    interaction="unary",
    method="get",
)


class Tags:
    """The tags in use on a brand's prompts"""

    def __init__(self, client: Client = client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    def list(
        self, brand_id: str, **options: Unpack[RequestOptions]
    ) -> ListBrandTagsResponse:
        """List a brand's tags

        Every tag in use on the brand's prompts, with how many carry each — enough to
        build the same filter the dashboard shows without paging the whole prompt list
        to derive it.

        Tags are not a resource of their own: a tag exists exactly as long as some
        prompt carries it. `branded` and `unbranded` are computed by Elmo and always
        listed.

        Args:
            brand_id: Brand identifier.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.tags import ListBrandTagsResponse

        call_options = group_params(
            [{"in": "path", "key": "brand_id", "map": "brandId"}], brand_id=brand_id
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, RequestOptions))
        )
        return send(
            self.client,
            LIST_BRAND_TAGS_DESCRIPTOR,
            call_options,
            ListBrandTagsResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> TagsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return TagsWithResponse(self)


class TagsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, tags: Tags) -> None:
        self._client = tags.client
        self.list = with_response(tags.list)


class AsyncTags:
    """The tags in use on a brand's prompts"""

    def __init__(self, client: AsyncClient = async_client) -> None:
        self.client = client
        """The client every call made through this object is sent with."""

    async def list(
        self, brand_id: str, **options: Unpack[AsyncRequestOptions]
    ) -> ListBrandTagsResponse:
        """List a brand's tags

        Every tag in use on the brand's prompts, with how many carry each — enough to
        build the same filter the dashboard shows without paging the whole prompt list
        to derive it.

        Tags are not a resource of their own: a tag exists exactly as long as some
        prompt carries it. `branded` and `unbranded` are computed by Elmo and always
        listed.

        Args:
            brand_id: Brand identifier.
            **options: What one call may set for itself, overriding the client it goes through.
        """

        from ..types.tags import ListBrandTagsResponse

        call_options = group_params(
            [{"in": "path", "key": "brand_id", "map": "brandId"}], brand_id=brand_id
        )
        call_options = merge_params(
            call_options, rename_options(keyword_options(options, AsyncRequestOptions))
        )
        return await async_send(
            self.client,
            LIST_BRAND_TAGS_DESCRIPTOR,
            call_options,
            ListBrandTagsResponse.model_validate,
        )

    @cached_property
    def with_response(self) -> AsyncTagsWithResponse:
        """The same calls, answering with the reply as well as what it decoded."""

        return AsyncTagsWithResponse(self)


class AsyncTagsWithResponse:
    """The same calls, answering with the reply as well as what it decoded."""

    def __init__(self, tags: AsyncTags) -> None:
        self._client = tags.client
        self.list = async_with_response(tags.list)
