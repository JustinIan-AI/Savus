"""Compatibility alias for the TUI backend events module."""

from __future__ import annotations

import sys

from loopdesk.cli.tui.backend import events as _target

sys.modules[__name__] = _target
