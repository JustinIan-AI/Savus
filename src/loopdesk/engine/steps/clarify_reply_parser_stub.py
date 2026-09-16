"""DEPRECATED — superseded by ``loopdesk.skills.meta.clarify_text``.

This file existed only to unblock PR3 wiring while the real
deterministic parser was being designed. PR4 ships the real parser
in ``loopdesk.skills.meta.clarify_text`` and ``meta_resolution.py``
now imports from there directly.

The re-export below is kept so any external caller that pinned the
PR3 import path still works; new code MUST import from
``loopdesk.skills.meta.clarify_text``.
"""

from __future__ import annotations

from loopdesk.skills.meta.clarify_text import parse_clarify_reply

__all__ = ["parse_clarify_reply"]
