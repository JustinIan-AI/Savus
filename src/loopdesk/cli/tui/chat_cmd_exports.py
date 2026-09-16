"""Compatibility alias for chat command legacy exports."""

from __future__ import annotations

import sys

from loopdesk.cli.tui.adapters import chat_cmd_exports as _target

sys.modules[__name__] = _target
