from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, Protocol, SupportsIndex, TypedDict

from typing_extensions import TypeVar

from .backoff import Jitter, RetryAfterHeader

BodyPayload = bytes | None


@dataclass
class EncodedBody:
    payload: BodyPayload
    content_type: str | None = None


Metadata = dict[str, str]


@dataclass
class Result:
    """One reply, as far as it has been read."""

    data: Any = None
    """The decoded body of a 2xx reply."""
    error: Any = None
    """The decoded body of a reply that failed."""
    response: Any = None
    """The reply itself, where one arrived."""


class CallLog(Protocol):
    def failed(self, error: BaseException) -> None: ...

    def replied(self, response: Any) -> None: ...

    def retrying(
        self, wait: float, retry: int, retries: int, after: Result | None = None
    ) -> None: ...

    def sending(self) -> None: ...


Interaction = str


@dataclass
class AuthScheme:
    """One way the API takes a credential, as the API description declares it."""

    type: str
    """`apiKey` sends the credential as it is, where `location` and `name` say.
    `http` sends it in the `Authorization` header, written as `scheme` says.

    """
    location: str = "header"
    """Where the credential is sent: `header`, `query` or `cookie`."""
    name: str = "Authorization"
    """The header, query parameter or cookie the credential is sent in."""
    key: str | None = None
    """Which credential this is. Its option, where it has one, has the same name."""
    scheme: str | None = None
    """How an `http` credential is written in the `Authorization` header: `basic` or
    `bearer`.

    """


AuthRequirement = AuthScheme | Sequence[AuthScheme]


class PhasedTimeout(Protocol):
    """A limit for each phase of one attempt, such as the HTTP library's `Timeout`.

    The HTTP library applies each one, and nothing limits the attempt as a whole.
    """

    connect: float | None
    pool: float | None
    read: float | None
    write: float | None


CallTimeout = float | Literal[False] | PhasedTimeout
"""A time limit in seconds, `False` for none, or a limit for each phase."""


@dataclass
class PaginationDescriptor:
    style: str
    cursor: str | None = None
    location: str = "query"
    items: str | None = None
    limit_param: str | None = None
    link: str | None = None
    more: str | None = None
    param: str | None = None
    pages: str | None = None
    size: str | None = None
    start: int | None = None
    total: str | None = None


class RetryRules(TypedDict, total=False):
    """How a failed call is sent again. Anything left out keeps the client's rule."""

    budget: float
    """How long a call may keep trying, in seconds, counted from the first
    attempt with the waits included. A retry that would start past it is not
    sent, and the last reply or error stands. An attempt that is running is not
    cut short: `timeout` limits each one. No limit by default.

    """
    delay: float
    """The first wait, in seconds, doubled for each attempt after it. Half a
    second by default.

    """
    jitter: Jitter
    """The share of each wait that is random. `"full"` by default."""
    max_delay: float
    """The longest computed wait, in seconds. Thirty by default."""
    max_retries: int
    """How many times a failed call is sent again, after the first attempt. Two
    by default.

    """
    max_retry_after: float
    """The longest wait the API may ask for, in seconds. Past it, the call gives
    up and hands back the reply as it is. Sixty by default.

    """
    methods: Sequence[str]
    """Methods that may be sent again. A request that never reached the API, a
    call carrying its API's idempotency key, and 408, 425 and 429 are sent again
    whatever this says. The idempotent methods by default.

    """
    retry_after: Sequence[RetryAfterHeader] | bool
    """Headers the API may name its own wait in, read before the backoff
    applies. `False` reads none.

    """
    retry_on_timeout: bool
    """Send the request again when an attempt runs past its deadline. Off by default."""
    statuses: Sequence[int]
    """Statuses worth another attempt. A reply with `x-should-retry: false` is
    never retried.

    """
    strategy: Literal["constant", "exponential"]
    """Whether each wait doubles, or stays at `delay`. `"exponential"` by default."""


class StyleSpec(TypedDict, total=False):
    explode: bool
    style: str


class ParameterSerialization(TypedDict, total=False):
    allow_reserved: bool
    array: StyleSpec
    media_type: str
    object: StyleSpec


class SerializationDescriptor(TypedDict, total=False):
    query: dict[str, ParameterSerialization]


@dataclass
class OperationDescriptor:
    address: str
    interaction: Interaction
    accept: str | None = None
    auth: Sequence[AuthRequirement] | None = None
    auth_optional: bool = False
    base_url: str | None = None
    deprecated: bool = False
    idempotency: str | None = None
    media_type: str | None = None
    method: str | None = None
    pagination: PaginationDescriptor | None = None
    retry: RetryRules | Literal[False] | None = None
    serialization: SerializationDescriptor | None = None
    timeout: CallTimeout | None = None


@dataclass
class Credential:
    location: str
    name: str
    value: str


@dataclass
class PlacedCredential:
    credential: Credential
    scheme: AuthScheme


@dataclass
class PreparedRequest:
    """A request about to be sent, which a `request` hook reads and may change."""

    address: Any
    """Where the request goes. Over HTTP, the whole URL, query string included."""
    interaction: Interaction
    """How the call exchanges messages, such as one request for one reply."""
    meta: Metadata
    """The headers to send, by lowercase name."""
    operation: OperationDescriptor
    """The operation this request calls, as declared, `method` included."""
    options: dict[str, Any]
    """The options this call resolved to: the client's, with the call's own on top."""
    attempt: int = 0
    """How many times this request was sent before."""
    body: BodyPayload = None
    """The request body, already encoded."""
    log: CallLog | None = None
    """Where this call writes its log records. Unset where the client does not log."""
    placed: Sequence[PlacedCredential] | None = None
    """Each credential put on the request, with the scheme it answers."""


AsyncSend = Callable[[PreparedRequest], Awaitable[Result]]


class RawResponse(Protocol):
    """The HTTP reply as the HTTP library hands it back."""

    @property
    def content(self) -> bytes: ...

    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def status_code(self) -> int: ...

    def json(self) -> Any: ...


class Binding(Protocol):
    accept: str | None
    name: str

    def apply_auth(self, credential: Credential, request: PreparedRequest) -> None: ...

    def read_error(
        self, result: Result, request: PreparedRequest
    ) -> BaseException | None: ...

    def resolve_address(
        self, operation: OperationDescriptor, options: dict[str, Any]
    ) -> Any: ...

    def read_result(self, raw: RawResponse, request: PreparedRequest) -> Result: ...


@dataclass
class FeatureContext:
    binding: Binding
    transport: Any


Send = Callable[[PreparedRequest], Result]


class Codec(Protocol):
    media_types: list[str]
    name: str

    def encode(self, value: Any) -> EncodedBody: ...


@dataclass
class CredentialSpec:
    option: bool = True
    prefix: str | None = None
    variable: str | None = None


class StreamResponse(Protocol):
    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def status_code(self) -> int: ...

    def close(self) -> None: ...

    def iter_bytes(self) -> Iterator[bytes]: ...

    def read(self) -> bytes: ...


AuthToken = str | None
"""A credential as a string, before it is written into the request. `None` sends
none.

"""


class RetryOptions(RetryRules, total=False):
    """The rules, and the caller's own functions that decide in their place."""

    retry_delay: Callable[[Result, PreparedRequest, int], float | None]
    """How long to wait before the next attempt, in seconds, in place of the
    API's retry headers and the backoff. `None` keeps the usual wait. After a
    failure that got no reply, the result holds only the `error`.
    `max_retry_after` does not limit what this returns.

    """
    retry_on: Callable[[Result, PreparedRequest], bool]
    """Whether to retry, in place of `statuses`, `x-should-retry` and
    `retry_on_timeout`. After a failure that got no reply, the result holds
    only the `error`. A call the API may have acted on is never asked about: a
    method outside `methods` is sent again only after 408, 425 or 429, or when
    the request never reached the API.

    """


RetryValue = RetryOptions | bool
"""How a failed call is retried: the rules, `True` for the client's own, or
`False` to send it once.

"""


TimeoutPolicy = Callable[[str, CallTimeout | None], CallTimeout | None]
"""Chooses the limit of one call, given the operation as `METHOD /path` and the
limit it would otherwise get. `None` keeps that limit.

"""


TimeoutValue = CallTimeout | TimeoutPolicy
"""A limit in seconds, `False` for none, or a policy choosing one per call."""


CredentialValue = str | Callable[[], AuthToken]
"""A credential, or a function that returns one when a call needs it."""


AuthResolver = Callable[[AuthScheme, AuthToken], AuthToken]
"""Returns the credential to send for `scheme`, given the value its option
holds. `None` sends none for that scheme.

"""


AuthValue = AuthResolver | Literal[False]
"""What the `auth` option takes: an `AuthResolver`, or `False` to send none."""


TItem_co = TypeVar("TItem_co", covariant=True)


class SequenceNotStr(Protocol[TItem_co]):
    """A list, a tuple, or any other sequence, but not a string or bytes."""

    def __getitem__(self, index: SupportsIndex, /) -> TItem_co: ...

    def __contains__(self, value: object, /) -> bool: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[TItem_co]: ...

    def __reversed__(self) -> Iterator[TItem_co]: ...

    def index(self, value: Any, start: int = 0, stop: int = ..., /) -> int: ...

    def count(self, value: Any, /) -> int: ...


AsyncCredentialValue = str | Callable[[], AuthToken | Awaitable[AuthToken]]
"""A credential, or a function that returns one when a call needs it. The function
may be async.

"""


AsyncAuthResolver = Callable[[AuthScheme, AuthToken], AuthToken | Awaitable[AuthToken]]
"""Returns the credential to send for `scheme`, given the value its option
holds. `None` sends none for that scheme.

"""


AsyncAuthValue = AsyncAuthResolver | Literal[False]
"""What the `auth` option takes: an `AsyncAuthResolver`, or `False` to send none."""
