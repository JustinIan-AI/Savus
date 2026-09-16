"""LoopDesk personal loop workspace package.

This package owns the v0.1 public surface for local-first personal loop
workspace state, layout, templates, and adapters. Legacy runtime modules
must stay behind adapter/facade boundaries and must not be imported from
this package's public API.
"""

from __future__ import annotations

from loopdesk.loop_workspace.helpers import ensure_loop_workspace
from loopdesk.loop_workspace.layout import LoopWorkspaceLayout
from loopdesk.loop_workspace.schema import LoopWorkspaceState, LoopWorkspaceStatus
from loopdesk.loop_workspace.service import LoopWorkspaceService
from loopdesk.loop_workspace.worktree import create_loop_worktree, remove_loop_worktree
from loopdesk.loop_workspace.templates import (
    PERSONAL_LOOP_TEMPLATES,
    list_personal_templates,
    load_personal_template,
)

__all__ = [
    "create_loop_worktree",
    "ensure_loop_workspace",
    "LoopWorkspaceLayout",
    "LoopWorkspaceService",
    "LoopWorkspaceState",
    "LoopWorkspaceStatus",
    "LoopWorktreeRecord",
    "remove_loop_worktree",
    "ensure_loop_workspace",
    "list_personal_templates",
    "load_personal_template",
    "PERSONAL_LOOP_TEMPLATES",
]
