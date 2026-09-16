"""Compatibility alias for the TUI-owned paste display helpers."""

from __future__ import annotations

import sys

from loopdesk.cli.tui import paste as _target

sys.modules[__name__] = _target
