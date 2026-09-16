"""Compatibility alias for the TUI-owned slash adapter bridge."""

from __future__ import annotations

import sys

from loopdesk.cli.tui import slash_bridge as _target

sys.modules[__name__] = _target
