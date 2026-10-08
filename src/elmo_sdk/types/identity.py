from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from .shared.common import OpenEnum


class APIKeyIdentityKeyType(str, OpenEnum):
    """`admin` for an instance key, `organization` for a dashboard-issued key."""

    ADMIN = "admin"
    ORGANIZATION = "organization"


class APIKeyIdentityRateLimitWindow(str, OpenEnum):
    MINUTE = "minute"
    HOUR = "hour"


class APIKeyIdentityRateLimit(BaseModel):
    """The key's configured limit — generous by design: it exists to stop a runaway
    loop, not to meter normal use. Enforcement is a fixed window and approximate under
    concurrency."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="allow")
    limit: int
    window: APIKeyIdentityRateLimitWindow


class APIKeyIdentityScopesItem(str, OpenEnum):
    READ = "read"
    WRITE = "write"


class APIKeyIdentity(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_by_name=True, use_attribute_docstrings=True, extra="allow"
    )
    brand_ids: list[str] | None = Field(
        ..., validation_alias="brandIds", serialization_alias="brandIds"
    )
    """Brands the key is narrowed to, or null when it reaches every brand in its
    organization. Never an empty array — a restriction to no brands is rejected at
    creation rather than treated as no restriction."""
    created_at: datetime | None = Field(
        ..., validation_alias="createdAt", serialization_alias="createdAt"
    )
    created_by: str | None = Field(
        ..., validation_alias="createdBy", serialization_alias="createdBy"
    )
    """The key's label, as given when it was issued. Null for admin keys."""
    expires_at: datetime | None = Field(
        ..., validation_alias="expiresAt", serialization_alias="expiresAt"
    )
    """When the key stops working, if it has an expiry."""
    key_type: APIKeyIdentityKeyType = Field(
        ..., validation_alias="keyType", serialization_alias="keyType"
    )
    """`admin` for an instance key, `organization` for a dashboard-issued key."""
    last_used_at: datetime | None = Field(
        ..., validation_alias="lastUsedAt", serialization_alias="lastUsedAt"
    )
    organization_id: str | None = Field(
        ..., validation_alias="organizationId", serialization_alias="organizationId"
    )
    """The organization this key acts inside. Null for admin keys."""
    organization_name: str | None = Field(
        ..., validation_alias="organizationName", serialization_alias="organizationName"
    )
    rate_limit: APIKeyIdentityRateLimit | None = Field(
        ..., validation_alias="rateLimit", serialization_alias="rateLimit"
    )
    """The key's configured limit — generous by design: it exists to stop a runaway
    loop, not to meter normal use. Enforcement is a fixed window and approximate under
    concurrency."""
    scopes: list[APIKeyIdentityScopesItem]
    """Scopes this key holds. A read-write key lists both; an admin key always does."""


GetMeResponse = APIKeyIdentity
"""Describe the calling key"""
