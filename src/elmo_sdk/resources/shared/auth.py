from __future__ import annotations

from ..._internal.core.types import AuthScheme

API_KEY_REQUIREMENTS = [AuthScheme(type="http", key="api_key", scheme="bearer")]
