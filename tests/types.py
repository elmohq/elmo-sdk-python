from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import assert_type

from elmo_sdk.types import APIKeyIdentity, ModelList

if TYPE_CHECKING:
    from elmo_sdk import Elmo


def returns_the_reply_each_call_declares(client: Elmo) -> None:
    assert_type(client.me.get(), APIKeyIdentity)
    assert_type(client.models.list(), ModelList)


def refuses_a_call_without_the_arguments_it_needs(client: Elmo) -> None:
    client.brands.create()  # ty: ignore[missing-argument]
    client.brands.get()  # ty: ignore[missing-argument]
    client.brands.update()  # ty: ignore[missing-argument]
    client.brands.analytics.get()  # ty: ignore[missing-argument]
    client.brands.citations.domains.list()  # ty: ignore[missing-argument]
    client.brands.citations.urls.list()  # ty: ignore[missing-argument]
    client.brands.opportunities.get()  # ty: ignore[missing-argument]
    client.brands.prompt_performance.list()  # ty: ignore[missing-argument]
    client.brands.query_fanout.get()  # ty: ignore[missing-argument]
    client.brands.tags.list()  # ty: ignore[missing-argument]
    client.competitors.create()  # ty: ignore[missing-argument]
    client.competitors.delete()  # ty: ignore[missing-argument]
    client.competitors.get()  # ty: ignore[missing-argument]
    client.competitors.update()  # ty: ignore[missing-argument]
    client.organizations.get()  # ty: ignore[missing-argument]
    client.organizations.billing.get()  # ty: ignore[missing-argument]
    client.prompts.create()  # ty: ignore[missing-argument]
    client.prompts.delete()  # ty: ignore[missing-argument]
    client.prompts.get()  # ty: ignore[missing-argument]
    client.prompts.update()  # ty: ignore[missing-argument]
    client.prompts.runs.list()  # ty: ignore[missing-argument]
    client.prompts.runs.get()  # ty: ignore[missing-argument]
    client.prompts.snapshot.get()  # ty: ignore[missing-argument]
    client.reports.create()  # ty: ignore[missing-argument]
    client.reports.get()  # ty: ignore[missing-argument]
    client.tools.analyze()  # ty: ignore[missing-argument]
