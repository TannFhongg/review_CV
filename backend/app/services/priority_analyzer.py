"""Priority ranking and Top 5 recommendations analyzer."""

from app.domain.enums import MatchStatus, Priority
from app.domain.models import RequirementMatch


class PriorityAnalyzer:
    """Analyzes and ranks recommendations by priority, extracting Top 5 actionable items."""

    PRIORITY_ORDER = {
        Priority.MUST_FIX: 1,
        Priority.SHOULD_FIX: 2,
        Priority.NICE_TO_HAVE: 3,
        Priority.ALREADY_STRONG: 4,
    }

    @classmethod
    def sort_by_priority(cls, matches: list[RequirementMatch]) -> list[RequirementMatch]:
        """Sort matches by priority (MUST_FIX first, then SHOULD_FIX, etc.)."""
        return sorted(
            matches,
            key=lambda m: (
                cls.PRIORITY_ORDER.get(m.priority, 5),
                0 if m.status == MatchStatus.MISSING else 1,
            ),
        )

    @classmethod
    def get_top_recommendations(
        cls,
        matches: list[RequirementMatch],
        limit: int = 5,
    ) -> list[RequirementMatch]:
        """Extract top N highest impact recommendations.

        Excludes ALREADY_STRONG matches as they require no action.
        Prioritizes items that need fixing.
        """
        actionable = [
            m for m in matches
            if m.priority != Priority.ALREADY_STRONG and m.recommendation
        ]

        sorted_actionable = cls.sort_by_priority(actionable)
        return sorted_actionable[:limit]
