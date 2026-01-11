"""
Simple router for XHS Text Agent.
Determines current view based on state. No LLM calls.
"""

from typing import Literal
from .state import AppState


ViewType = Literal[
    "onboarding_niche",
    "onboarding_goal", 
    "onboarding_style",
    "onboarding_effort",
    "onboarding_constraints",
    "onboarding_custom",
    "ready_to_generate",
    "weekly_plan",
    "view_day",
    "rewrite_day",
    "weekly_review"
]


def get_current_view(state: AppState) -> ViewType:
    """
    Determine which view to show based on current state.
    This is a pure function with no side effects or LLM calls.
    """
    # If we have a weekly plan, show plan-related views
    if state.weekly_plan:
        if state.viewing_day is not None:
            return "view_day"
        if state.rewriting_day is not None:
            return "rewrite_day"
        return "weekly_plan"
    
    # Onboarding flow
    if state.niche is None:
        return "onboarding_niche"
    if state.goal is None:
        return "onboarding_goal"
    if state.style is None:
        return "onboarding_style"
    if state.effort is None:
        return "onboarding_effort"
    
    # Constraints and custom are optional, check step marker
    if state.current_step == "constraints":
        return "onboarding_constraints"
    if state.current_step == "custom":
        return "onboarding_custom"
    
    # All onboarding complete, ready to generate
    if state.is_onboarding_complete():
        return "ready_to_generate"
    
    # Fallback
    return "onboarding_niche"


def advance_onboarding(state: AppState) -> None:
    """
    Advance to the next onboarding step.
    Modifies state in place.
    """
    current = state.current_step
    
    if current == "niche":
        state.current_step = "goal"
    elif current == "goal":
        state.current_step = "style"
    elif current == "style":
        state.current_step = "effort"
    elif current == "effort":
        state.current_step = "constraints"
    elif current == "constraints":
        state.current_step = "custom"
    elif current == "custom":
        state.current_step = "ready"

