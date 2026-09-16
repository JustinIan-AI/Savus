"""Compatibility alias for the TUI-owned terminal renderer."""

from __future__ import annotations

import sys

from loopdesk.cli.tui import terminal_renderer as _target

sys.modules[__name__] = _target
