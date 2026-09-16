"""Gateway RPC package.

This package preserves the former flat RPC import surface verbatim: every existing

    from loopdesk.gateway.rpc import RpcContext, RpcDispatcher, get_dispatcher

still resolves, because the names are re-exported from
:mod:`loopdesk.gateway.rpc.registry`. The package additionally exposes
:class:`RpcRegistry` and :func:`get_registry` as the canonical names —
``RpcDispatcher``/``get_dispatcher`` are thin shims.

Sibling modules ``loopdesk.gateway.rpc_*`` live outside this package and are
imported below so their handler registrations execute at boot time, which
is what the original ``rpc.py`` did.
"""

from __future__ import annotations

from loopdesk.gateway.rpc.registry import (
    RpcContext,
    RpcDispatcher,
    RpcHandlerError,
    RpcHandlerFn,
    RpcMethodEntry,
    RpcRegistry,
    RpcUnavailableError,
    ScopeDriftError,
    get_dispatcher,
    get_registry,
    validate_classification,
)

__all__ = [
    "RpcContext",
    "RpcDispatcher",
    "RpcHandlerError",
    "RpcHandlerFn",
    "RpcMethodEntry",
    "RpcRegistry",
    "RpcUnavailableError",
    "ScopeDriftError",
    "get_dispatcher",
    "get_registry",
    "validate_classification",
]

# Import sibling submodules to trigger handler registration against the
# module-level singleton. The import surface intentionally omits the deprecated
# product RPC methods listed in ``REMOVED_PRODUCT_METHODS`` in
# tests/test_gateway/test_rpc_extended.py. These methods MUST NOT register
# handlers at boot — the release surface is contracted to reject them with
# METHOD_NOT_FOUND.
import loopdesk.gateway.rpc_agents  # noqa: E402, F401
import loopdesk.gateway.rpc_approvals  # noqa: E402, F401
import loopdesk.gateway.rpc_channels  # noqa: E402, F401
import loopdesk.gateway.rpc_chat  # noqa: E402, F401
import loopdesk.gateway.rpc_commands  # noqa: E402, F401
import loopdesk.gateway.rpc_config  # noqa: E402, F401
import loopdesk.gateway.rpc_cron  # noqa: E402, F401
import loopdesk.gateway.rpc_diagnostics  # noqa: E402, F401
import loopdesk.gateway.rpc_doctor  # noqa: E402, F401
import loopdesk.gateway.rpc_logs  # noqa: E402, F401
import loopdesk.gateway.rpc_memory  # noqa: E402, F401
import loopdesk.gateway.rpc_models  # noqa: E402, F401
import loopdesk.gateway.rpc_onboarding  # noqa: E402, F401
import loopdesk.gateway.rpc_proposals  # noqa: E402, F401
import loopdesk.gateway.rpc_secrets  # noqa: E402, F401
import loopdesk.gateway.rpc_sessions  # noqa: E402, F401
import loopdesk.gateway.rpc_skills  # noqa: E402, F401
import loopdesk.gateway.rpc_system  # noqa: E402, F401
import loopdesk.gateway.rpc_tools  # noqa: E402, F401
import loopdesk.gateway.rpc_usage  # noqa: E402, F401
import loopdesk.gateway.rpc_wizard  # noqa: E402, F401
import loopdesk.gateway.rpc_loop_workspace  # noqa: E402, F401

# Fail fast if any registered handler disagrees with ``gateway.scopes``.
validate_classification()
