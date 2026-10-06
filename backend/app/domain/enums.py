"""Domain enums."""

from enum import StrEnum


class MatchStatus(StrEnum):
    """Match status between a JD requirement and CV evidence."""
    STRONG = "strong_match"
    PARTIAL = "partial_match"
    WEAK = "weak_evidence"
    MISSING = "missing"
    UNKNOWN = "unknown"


class Priority(StrEnum):
    """Priority level for a recommendation."""
    MUST_FIX = "must_fix"           # 🔴
    SHOULD_FIX = "should_fix"       # 🟠
    NICE_TO_HAVE = "nice_to_have"   # 🟡
    ALREADY_STRONG = "already_strong"  # 🟢


class Importance(StrEnum):
    """Importance level of a JD requirement."""
    REQUIRED = "required"
    PREFERRED = "preferred"
    NICE_TO_HAVE = "nice_to_have"


class SkillCategory(StrEnum):
    """Category of a skill."""
    TECHNICAL = "technical"
    SOFT = "soft"
    TOOL = "tool"
    DOMAIN = "domain"
