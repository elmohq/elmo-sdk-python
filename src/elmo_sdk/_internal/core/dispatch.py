from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, NoReturn

from ..codec.registry import encode_named_body
from .config import merge_configs
from .env import read_defaults, with_implied_environment
from .errors import UnsupportedInteractionError, to_transport_error, unsendable_header
from .features import (
    Feature,
    run_async_error,
    run_async_prepare,
    run_async_request,
    run_async_result,
    run_error,
    run_options,
    run_prepare,
    run_request,
    run_result,
    wrap_async_send,
    wrap_send,
)
from .metadata import merge_metadata, stack_metadata, unsendable_name
from .protocol import only_protocol, transport_method
from .types import (
    Binding,
    Codec,
    CredentialSpec,
    FeatureContext,
    OperationDescriptor,
    PreparedRequest,
    Result,
)


@dataclass
class DispatchSetup:
    protocols: dict[str, Any]
    codecs: list[Codec] = field(default_factory=lambda: [])
    credentials: dict[str, CredentialSpec] = field(default_factory=lambda: {})
    defaults: dict[str, Any] = field(default_factory=lambda: {}, repr=False)
    env: dict[str, str] = field(default_factory=lambda: {})
    features: list[Feature] = field(default_factory=lambda: [])
    overrides: dict[str, Any] = field(default_factory=lambda: {}, repr=False)
    env_defaults: dict[str, Any] | None = field(
        default=None, init=False, repr=False, compare=False
    )
    merged_defaults: dict[str, Any] | None = field(
        default=None, init=False, repr=False, compare=False
    )


def build_request_without_cookies(
    setup: DispatchSetup, operation: OperationDescriptor, resolved: dict[str, Any]
) -> PreparedRequest:
    binding, _ = only_protocol(setup.protocols, operation.interaction)
    encoded = encode_named_body(setup.codecs, operation.media_type, resolved)
    meta = merge_metadata(resolved.get("headers"))
    if encoded is not None and encoded.content_type and "content-type" not in meta:
        meta["content-type"] = encoded.content_type
    accept = operation.accept or binding.accept
    if accept and "accept" not in meta:
        meta["accept"] = accept
    return PreparedRequest(
        address=binding.resolve_address(operation, resolved),
        body=encoded.payload if encoded is not None else None,
        interaction=operation.interaction,
        meta=meta,
        operation=operation,
        options=resolved,
    )


def defaults_of(setup: DispatchSetup) -> dict[str, Any]:
    if setup.merged_defaults is None:
        if setup.env_defaults is None:
            setup.env_defaults = read_defaults(setup.env, setup.credentials)
        setup.merged_defaults = merge_configs(
            setup.defaults, setup.env_defaults, setup.overrides
        )
    return setup.merged_defaults


def resolve_options(
    setup: DispatchSetup, options: dict[str, Any] | None
) -> dict[str, Any]:
    own = with_implied_environment(options or {}, setup.credentials)
    return merge_configs(defaults_of(setup), own)


def _built(
    setup: DispatchSetup, operation: OperationDescriptor, options: dict[str, Any] | None
) -> tuple[PreparedRequest, FeatureContext]:
    binding, transport = only_protocol(setup.protocols, operation.interaction)
    ctx = FeatureContext(binding=binding, transport=transport)
    resolved = resolve_options(setup, options)
    run_options(setup.features, resolved, operation, ctx)
    return build_request_without_cookies(setup, operation, resolved), ctx


def prepare(
    setup: DispatchSetup,
    operation: OperationDescriptor,
    options: dict[str, Any] | None = None,
) -> PreparedRequest:
    request, ctx = _built(setup, operation, options)
    run_prepare(setup.features, request, ctx)
    return request


def _finish(
    binding: Binding, result: Result, request: PreparedRequest, envelope: bool
) -> Any:
    failure = binding.read_error(result, request)
    if failure is not None:
        raise failure
    return result if envelope else result.data


def _raise(
    features: list[Feature],
    error: Exception,
    request: PreparedRequest,
    ctx: FeatureContext,
) -> NoReturn:
    named = run_error(features, error, request, ctx)
    if named is error:
        raise error
    raise named from error


def _send(transport: Any, request: PreparedRequest) -> Any:
    name = transport_method(request.interaction)
    method = getattr(transport, name, None)
    if not callable(method):
        raise UnsupportedInteractionError(transport.name, request.interaction, name)
    unsendable = unsendable_name(request.meta)
    if unsendable is not None:
        raise unsendable_header(unsendable)
    log = getattr(request, "log", None)
    if log is not None:
        log.sending()
    try:
        return method(request)
    except Exception as error:
        raise to_transport_error(error, request) from error


def _transport_for(setup: DispatchSetup, request: PreparedRequest) -> Any:
    _, protocol_transport = only_protocol(setup.protocols, request.interaction)
    return request.options.get("transport") or protocol_transport


def execute(
    setup: DispatchSetup, request: PreparedRequest, envelope: bool = False
) -> Any:
    binding, _ = only_protocol(setup.protocols, request.interaction)
    transport = _transport_for(setup, request)
    ctx = FeatureContext(binding=binding, transport=transport)

    def send(attempt: PreparedRequest) -> Result:
        run_request(setup.features, attempt, ctx)
        return binding.read_result(_send(transport, attempt), attempt)

    try:
        result = wrap_send(setup.features, send, ctx)(request)
        return _finish(
            binding, run_result(setup.features, result, request, ctx), request, envelope
        )
    except Exception as error:
        _raise(setup.features, error, request, ctx)


def dispatch(
    setup: DispatchSetup,
    operation: OperationDescriptor,
    options: dict[str, Any] | None = None,
    envelope: bool = False,
) -> Any:
    return execute(setup, prepare(setup, operation, options), envelope)


async def _async_raise(
    features: list[Feature],
    error: Exception,
    request: PreparedRequest,
    ctx: FeatureContext,
) -> NoReturn:
    named = await run_async_error(features, error, request, ctx)
    if named is error:
        raise error
    raise named from error


async def _async_send(transport: Any, request: PreparedRequest) -> Any:
    name = transport_method(request.interaction)
    method = getattr(transport, name, None)
    if not callable(method):
        raise UnsupportedInteractionError(transport.name, request.interaction, name)
    unsendable = unsendable_name(request.meta)
    if unsendable is not None:
        raise unsendable_header(unsendable)
    log = getattr(request, "log", None)
    if log is not None:
        log.sending()
    try:
        pending: Any = method(request)
        return await pending
    except Exception as error:
        raise to_transport_error(error, request) from error


async def async_execute(
    setup: DispatchSetup, request: PreparedRequest, envelope: bool = False
) -> Any:
    binding, _ = only_protocol(setup.protocols, request.interaction)
    transport = _transport_for(setup, request)
    ctx = FeatureContext(binding=binding, transport=transport)

    async def send(attempt: PreparedRequest) -> Result:
        await run_async_request(setup.features, attempt, ctx)
        return binding.read_result(await _async_send(transport, attempt), attempt)

    try:
        result = await wrap_async_send(setup.features, send, ctx)(request)
        return _finish(
            binding,
            await run_async_result(setup.features, result, request, ctx),
            request,
            envelope,
        )
    except Exception as error:
        await _async_raise(setup.features, error, request, ctx)


async def async_prepare(
    setup: DispatchSetup,
    operation: OperationDescriptor,
    options: dict[str, Any] | None = None,
) -> PreparedRequest:
    request, ctx = _built(setup, operation, options)
    await run_async_prepare(setup.features, request, ctx)
    return request


async def async_dispatch(
    setup: DispatchSetup,
    operation: OperationDescriptor,
    options: dict[str, Any] | None = None,
    envelope: bool = False,
) -> Any:
    request = await async_prepare(setup, operation, options)
    return await async_execute(setup, request, envelope)


def own_transport(
    template: Any, client: Any | None = None, setup: DispatchSetup | None = None
) -> Any:
    if client is None and setup is not None:
        for carried in setup.protocols.values():
            transport = carried.get("transport")
            if transport is not None and transport is not template:
                return transport
    return replace(template, client=client)


def configure(setup: DispatchSetup, options: dict[str, Any]) -> DispatchSetup:
    stated = {key: value for key, value in options.items() if value is not None}
    stated = with_implied_environment(stated, setup.credentials)
    overrides = merge_configs(setup.overrides, stated)
    overrides["headers"] = stack_metadata(
        setup.overrides.get("headers"), stated.get("headers")
    )
    return replace(setup, overrides=overrides)


def with_transport(setup: DispatchSetup, transport: Any) -> DispatchSetup:
    protocols: dict[str, Any] = {}
    for name, carried in setup.protocols.items():
        protocols[name] = {**carried, "transport": transport}
    return replace(setup, protocols=protocols)
