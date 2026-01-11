"""
State management for XHS Text Agent.
Single state object stored in st.session_state.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class DayContent:
    """Content for a single day's post."""
    day: int
    title: str
    hook: str
    bullets: List[str]
    cta: str
    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "day": self.day,
            "title": self.title,
            "hook": self.hook,
            "bullets": self.bullets,
            "cta": self.cta,
            "tags": self.tags
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DayContent":
        return cls(
            day=data.get("day", 1),
            title=data.get("title", ""),
            hook=data.get("hook", ""),
            bullets=data.get("bullets", []),
            cta=data.get("cta", ""),
            tags=data.get("tags", [])
        )


@dataclass
class WeeklyReview:
    """Weekly review output."""
    reflection: str
    suggestions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reflection": self.reflection,
            "suggestions": self.suggestions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeeklyReview":
        return cls(
            reflection=data.get("reflection", ""),
            suggestions=data.get("suggestions", [])
        )


@dataclass
class AppState:
    """
    Main application state.
    Tracks onboarding progress, weekly plan, and review.
    """
    # Onboarding state
    current_step: str = "niche"  # niche, goal, style, effort, constraints, custom, ready
    niche: Optional[str] = None
    goal: Optional[str] = None
    style: Optional[str] = None
    effort: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    custom_note: str = ""

    # Content state
    weekly_plan: List[DayContent] = field(default_factory=list)
    is_generating: bool = False
    generation_error: Optional[str] = None

    # View state
    viewing_day: Optional[int] = None
    rewriting_day: Optional[int] = None
    rewrite_instruction: str = ""

    # Review state
    review_best_days: List[int] = field(default_factory=list)
    review_hardest_days: List[int] = field(default_factory=list)
    review_pace: str = ""
    review_notes: str = ""
    weekly_review: Optional[WeeklyReview] = None
    is_reviewing: bool = False
    review_error: Optional[str] = None

    def is_onboarding_complete(self) -> bool:
        """Check if all required onboarding steps are done."""
        return all([
            self.niche is not None,
            self.goal is not None,
            self.style is not None,
            self.effort is not None
        ])

    def get_onboarding_summary(self) -> Dict[str, Any]:
        """Get summary of onboarding choices for prompts."""
        return {
            "niche": self.niche,
            "goal": self.goal,
            "style": self.style,
            "effort": self.effort,
            "constraints": self.constraints,
            "custom_note": self.custom_note
        }

    def reset_content(self):
        """Reset content-related state."""
        self.weekly_plan = []
        self.viewing_day = None
        self.rewriting_day = None
        self.rewrite_instruction = ""
        self.generation_error = None
        self.weekly_review = None
        self.review_error = None

    def reset_all(self):
        """Reset entire state."""
        self.current_step = "niche"
        self.niche = None
        self.goal = None
        self.style = None
        self.effort = None
        self.constraints = []
        self.custom_note = ""
        self.reset_content()
        self.review_best_days = []
        self.review_hardest_days = []
        self.review_pace = ""
        self.review_notes = ""


def get_state() -> AppState:
    """Get or initialize the app state from session_state."""
    import streamlit as st
    if "app_state" not in st.session_state:
        st.session_state.app_state = AppState()
    return st.session_state.app_state


def update_state(state: AppState):
    """Update the state in session_state."""
    import streamlit as st
    st.session_state.app_state = state

