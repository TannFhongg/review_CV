"""Gap analysis service for evaluating candidate deficiencies and strengths."""

from pydantic import BaseModel

from app.domain.enums import MatchStatus, Priority
from app.domain.models import RequirementMatch


class GapSummary(BaseModel):
    """Statistical summary of match statuses and prioritized counts."""
    strong_count: int
    partial_count: int
    weak_count: int
    missing_count: int
    must_fix_count: int
    should_fix_count: int
    nice_to_have_count: int
    already_strong_count: int


class GapAnalyzer:
    """Analyzes requirements matches to extract statistical summaries and gaps."""

    @staticmethod
    def summarize(matches: list[RequirementMatch]) -> GapSummary:
        """Calculate counts across all match statuses and priority levels."""
        strong = sum(1 for m in matches if m.status == MatchStatus.STRONG)
        partial = sum(1 for m in matches if m.status == MatchStatus.PARTIAL)
        weak = sum(1 for m in matches if m.status == MatchStatus.WEAK)
        missing = sum(1 for m in matches if m.status == MatchStatus.MISSING)

        must_fix = sum(1 for m in matches if m.priority == Priority.MUST_FIX)
        should_fix = sum(1 for m in matches if m.priority == Priority.SHOULD_FIX)
        nice_to_have = sum(1 for m in matches if m.priority == Priority.NICE_TO_HAVE)
        already_strong = sum(1 for m in matches if m.priority == Priority.ALREADY_STRONG)

        return GapSummary(
            strong_count=strong,
            partial_count=partial,
            weak_count=weak,
            missing_count=missing,
            must_fix_count=must_fix,
            should_fix_count=should_fix,
            nice_to_have_count=nice_to_have,
            already_strong_count=already_strong,
        )

    @staticmethod
    def filter_gaps(matches: list[RequirementMatch]) -> list[RequirementMatch]:
        """Return all matches that represent gaps (missing, weak, partial)."""
        return [
            m for m in matches
            if m.status in {MatchStatus.MISSING, MatchStatus.WEAK, MatchStatus.PARTIAL}
        ]

    @staticmethod
    def get_strong_matches(matches: list[RequirementMatch]) -> list[RequirementMatch]:
        """Return matches where candidate is already strong."""
        return [m for m in matches if m.status == MatchStatus.STRONG]
