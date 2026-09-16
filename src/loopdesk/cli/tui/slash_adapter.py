"""Compatibility alias for the gateway slash adapter."""

from __future__ import annotations

import sys

from loopdesk.cli.tui.adapters import slash_gateway as _target

sys.modules[__name__] = _target
