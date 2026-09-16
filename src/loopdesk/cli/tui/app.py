"""Compatibility alias for the terminal TUI application."""

from __future__ import annotations

import sys

from loopdesk.cli.tui.terminal import app as _target

sys.modules[__name__] = _target
