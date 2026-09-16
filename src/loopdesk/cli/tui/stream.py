"""Compatibility alias for terminal stream rendering primitives."""

from __future__ import annotations

import sys

from loopdesk.cli.tui.terminal import stream as _target

sys.modules[__name__] = _target
