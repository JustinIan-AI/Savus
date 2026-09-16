"""Skills system for LoopDesk.

Six-layer architecture (low→high precedence):
- Extra: config-specified additional directories
- Bundled: Ship with LoopDesk in src/loopdesk/skills/bundled/
- Managed: Local installs in $LOOPDESK_STATE_DIR/skills/ (default ~/.loopdesk/skills/)
- Personal: Local user installs in ~/.agents/skills/
- Project: {workspace}/.agents/skills/
- Workspace: {workspace}/skills/

Only Bundled skills are shipped with LoopDesk. Managed, Personal, Project,
Workspace, and Extra layers are local directories discovered at runtime.
"""

from __future__ import annotations

from loopdesk.skills.eligibility import (
    EligibilityContext,
    EligibilityReport,
    InstallHint,
    check_eligibility,
    diagnose_eligibility,
)
from loopdesk.skills.injector import SkillInjector
from loopdesk.skills.loader import SkillLoader
from loopdesk.skills.resources import SkillResources
from loopdesk.skills.types import (
    SkillInstallSpec,
    SkillLayer,
    SkillPlatformMeta,
    SkillRequires,
    SkillSpec,
)

__all__ = [
    "EligibilityContext",
    "EligibilityReport",
    "InstallHint",
    "SkillInjector",
    "SkillInstallSpec",
    "SkillLayer",
    "SkillLoader",
    "SkillPlatformMeta",
    "SkillRequires",
    "SkillResources",
    "SkillSpec",
    "check_eligibility",
    "diagnose_eligibility",
]
