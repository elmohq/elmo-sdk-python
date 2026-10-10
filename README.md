# Elmo Python SDK

[![PyPI](https://img.shields.io/pypi/v/elmo-sdk)](https://pypi.org/project/elmo-sdk/) [![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/elmohq/elmo-sdk-python/blob/HEAD/LICENSE.md)

Read and manage the brands, prompts, competitors, and AI-visibility analytics of this deployment.

This package calls the Elmo API from Python, with a synchronous and an asynchronous client built on `httpx2`. It includes Pydantic models for every request and reply.

[Issues](https://github.com/elmohq/elmo-sdk-python/issues)

## Installation

The SDK is published on [PyPI](https://pypi.org/project/elmo-sdk/). Install it with the package manager you use.

```sh
uv add elmo-sdk
```

<details>
<summary>Other package managers</summary>

```sh
pip install elmo-sdk
```

```sh
poetry add elmo-sdk
```

```sh
pdm add elmo-sdk
```

</details>

## Usage

Set `ELMO_API_KEY` in your environment, then call the API:

```python
from elmo_sdk import Elmo

elmo = Elmo()
data = elmo.brands.list()

print(data)
```

<details>
<summary>The same call with AsyncElmo</summary>

```python
import asyncio

from elmo_sdk import AsyncElmo

async_elmo = AsyncElmo()


async def main() -> None:
    data = await async_elmo.brands.list()

    print(data)


asyncio.run(main())
```

</details>

## Requirements

- Python 3.10 or later

## Pagination

Iterate a paginated call to read every item. Each page is fetched when the loop reaches it.

```python
from elmo_sdk import Elmo

elmo = Elmo()
for item in elmo.brands.list():
    print(item)
```

## Errors

When the API answers with an error status, the call raises `APIError`, or a subclass named for the status. `data` holds the body as the model its status declares, where there is one. `request_id` holds the id to quote when you report a failure. Every exception a call raises subclasses `ElmoError`.

```python
from elmo_sdk import APIError, Elmo

elmo = Elmo()
try:
    elmo.brands.list()
except APIError as error:
    print(error.status, error.request_id, error.data)
```

An argument the call refuses raises `ElmoError` itself, before anything is sent, with pydantic's error as its `__cause__`. A model you build yourself raises `pydantic.ValidationError`, as any pydantic model does.

Catch one status by its class:

| Status                 | Error                      |
| ---------------------- | -------------------------- |
| 400                    | `BadRequestError`          |
| 401                    | `AuthenticationError`      |
| 402                    | `PaymentRequiredError`     |
| 403                    | `PermissionDeniedError`    |
| 404                    | `NotFoundError`            |
| 409                    | `ConflictError`            |
| 422                    | `UnprocessableEntityError` |
| 429                    | `RateLimitError`           |
| 500 and above          | `InternalServerError`      |
| Any other error status | `APIError`                 |

A call that got no reply has no status. It raises `TransportError`, or `TransportTimeoutError` where an attempt ran out of time. Neither is an `APIError`.

A call made with no credential raises `MissingCredentialError` before anything is sent. A reply the SDK cannot read raises `DecodeError`.

By the time a call raises `RateLimitError`, the client has sent it again up to 2 times. `retry_after_seconds` on `RateLimitError` holds how long the API asked to wait, in seconds, where it said.

To report a failure, [open an issue](https://github.com/elmohq/elmo-sdk-python/issues) and quote `request_id`.

## Configuration

### Authentication

Get an API key from the Elmo dashboard, under **Organization Settings → API Keys**.

The client reads `ELMO_API_KEY` from the environment. To pass the value yourself, set `api_key`:

```python
from elmo_sdk import Elmo

elmo = Elmo(api_key="elmo_…")
```

`api_key` also takes a function that returns the value, such as one that reads it from a secret store. The client calls it for each request.

### Base URL

Calls go to `/api/v1`. To send them elsewhere, such as a proxy or a gateway, set `base_url`, or the `ELMO_BASE_URL` environment variable:

```python
from elmo_sdk import Elmo

elmo = Elmo(base_url="https://gateway.example.com")
```

### Closing the client

The client opens a connection pool on its first call, and a `with` block closes it on the way out. A client that lives as long as the process closes with `close()` when you shut down. `AsyncElmo` closes with `async with` and `aclose()`. A client you passed as `http_client` is yours to close.

```python
from elmo_sdk import Elmo

with Elmo() as elmo:
    elmo.brands.list()
```

<details>
<summary>The same with AsyncElmo</summary>

```python
import asyncio

from elmo_sdk import AsyncElmo


async def main() -> None:
    async with AsyncElmo() as async_elmo:
        await async_elmo.brands.list()


asyncio.run(main())
```

</details>

### Per-call options

One call can run under settings of its own. `with_options` returns a client that differs only in what you pass and sends over the same connection pool, and takes every option the client does. Headers merge per name, and every other option replaces the client's:

```python
from elmo_sdk import Elmo

elmo = Elmo()
elmo.with_options(timeout=5, max_retries=0).brands.list()
```

A call also takes the same settings as keyword arguments:

```python
from elmo_sdk import Elmo

elmo = Elmo()
elmo.brands.list(timeout=5, max_retries=0)
```

### Retries

A failed call is sent again up to 2 times, after a lost connection, a 408, 425 or 429 status, or most 5xx statuses. A `POST` or `PATCH` call may already have changed something, so it is sent again only after a request that never reached the API or a 408, 425 or 429 status.

Each wait is longer than the last on average, or as long as `Retry-After` asks.

To change that count, set `max_retries` on the client or on one call. For every other rule, such as which failures are retried and how long each wait is, set `retry`, which takes a `RetryOptions`:

```python
from elmo_sdk import Elmo

elmo = Elmo(max_retries=5)
elmo.with_options(max_retries=0).brands.list()
```

To wait longer between attempts, set the first wait and the longest one:

```python
from elmo_sdk import Elmo

elmo = Elmo(retry={"delay": 1, "max_delay": 10})
```

### Timeouts

Each attempt may run for NaN seconds. One that runs longer raises `TransportTimeoutError`. To change the limit, set `timeout` in seconds on the client or on one call. `False` removes it:

```python
from elmo_sdk import Elmo

elmo = Elmo(timeout=20)
elmo.with_options(timeout=5).brands.list()
```

### Logging

Logging is off by default. To see what the SDK sends and receives, set `log_level` or the `ELMO_LOG` environment variable. `"info"` logs each call and its reply, and `"debug"` adds headers, with credentials redacted. Bodies are never logged. Records go to a logger under `elmo_sdk`, which writes to standard error until the application configures logging. Pass `logger` to use your own.

```python
from elmo_sdk import Elmo

elmo = Elmo(log_level="info")
```

### Custom HTTP client

To send requests over HTTP/2, through a proxy, or with other TLS settings or connection limits, pass an `httpx2.Client` you built as `http_client`. HTTP/2 needs the `httpx2[http2]` extra. A plain `httpx.Client` (or `httpx.AsyncClient`) works here too, since the two share their shape. `AsyncElmo` takes an `httpx2.AsyncClient`.

```python
import httpx2
from elmo_sdk import Elmo

elmo = Elmo(http_client=httpx2.Client(http2=True))
```

### Default headers

To send a header with every call, set `default_headers` on the client. A call's own `extra_headers` are merged with them by name, and `None` drops one:

```python
from elmo_sdk import Elmo

elmo = Elmo(default_headers={"x-team": "billing"})
```

### Interceptors

To run code of your own around every call, set `interceptors` on the client. A `request` hook runs on each request last before it is sent, with the credential already on it. A `response` hook returns the result the caller reads, and an `error` hook returns the error the caller gets, so a hook that only observes returns what it was given. Hooks run in the order you list them. `AsyncElmo` also waits for a hook that returns an awaitable.

```python
from elmo_sdk import Elmo, PreparedRequest


def tag(request: PreparedRequest) -> None:
    request.meta["x-request-source"] = "worker"


elmo = Elmo(interceptors={"request": [tag]})
```

### Raw response

To read the HTTP response as well, make the call through `with_response`. What comes back holds:

- `data`: what the call returns on its own
- `status`: the status it arrived with
- `request_id`: the id to quote when you report a problem
- `response`: the `httpx2.Response` itself, for a header or a field the SDK does not model

```python
from elmo_sdk import Elmo

elmo = Elmo()
reply = elmo.with_response.me.get()
print(reply.status, reply.response.headers)
```

### Environment variables

The client reads each variable when its option is not set:

| Variable        | Option      | Default     |
| --------------- | ----------- | ----------- |
| `ELMO_API_KEY`  | `api_key`   |             |
| `ELMO_BASE_URL` | `base_url`  | `"/api/v1"` |
| `ELMO_LOG`      | `log_level` | `"off"`     |

### Forward compatibility

The API can add a field or a value after this version of the SDK is released. This version keeps working when that happens, and you can use the new part of the API before a release declares it.

- A field of a reply that this version does not declare is kept. Read it from `model_extra` on the model that holds it.
- An enum value this version does not list is a member of its own, whose `value` is what the API sent.
- To send a field this version does not declare, pass it in `extra_body` to a call. A model or a dictionary you pass keeps any other key you set on it, and sends it.

## License

MIT. See [LICENSE.md](https://github.com/elmohq/elmo-sdk-python/blob/HEAD/LICENSE.md).
