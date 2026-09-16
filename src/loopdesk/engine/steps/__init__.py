"""Pre-turn pipeline steps."""

from loopdesk.engine.pipeline import TurnContext
from loopdesk.engine.steps.inject_platform_hint import inject_platform_hint
from loopdesk.engine.steps.inject_subagent_grounding import inject_subagent_grounding
from loopdesk.engine.steps.meta_resolution import meta_resolution
from loopdesk.engine.steps.prompt_cache import apply_prompt_cache
from loopdesk.engine.steps.reasoning_hint_observer import observe_reasoning_hint
from loopdesk.engine.steps.resolve_model import resolve_model
from loopdesk.engine.steps.skills_filter import filter_skills

try:
    from loopdesk.engine.steps.squilla_router import apply_squilla_router
except ImportError:

    async def apply_squilla_router(ctx: TurnContext) -> TurnContext:
        return ctx


__all__ = [
    "apply_prompt_cache",
    "apply_squilla_router",
    "filter_skills",
    "inject_platform_hint",
    "inject_subagent_grounding",
    "meta_resolution",
    "observe_reasoning_hint",
    "resolve_model",
]
