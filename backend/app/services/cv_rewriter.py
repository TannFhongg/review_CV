"""CV Rewriter service providing Before/After suggestions with strict factual grounding."""

import structlog
from pydantic import BaseModel

from app.domain.enums import MatchStatus, Priority
from app.domain.models import CVSuggestion, RequirementMatch, StructuredCV, StructuredJD
from app.providers.llm.base import LLMProvider

logger = structlog.get_logger()

CV_REWRITER_SYSTEM_PROMPT = """You are an elite Career Coach and Resume Engineering Specialist.
Your task is to propose high-impact Before/After rewrite suggestions for a candidate's CV to maximize alignment with a specific Job Description.

CRITICAL POLICY — STRICT NO FABRICATION:
1. The rewritten version MUST remain 100% factually supported by the candidate's original CV.
2. NEVER invent achievements, metrics, companies, years, or technologies that the candidate never mentioned.
3. If optimizing a project:
   - Clarify and emphasize the specific technologies already mentioned elsewhere in the CV (e.g., if the CV lists Qt Widgets in skills and a VTuber app in projects, emphasize 'Qt Widgets' and 'signals and slots' in the project bullet).
4. For any requirement where the candidate has no evidence:
   - Explicitly note: "Potential improvement — only add this if you genuinely have this experience."
   - Do NOT invent fake experience in the rewrite.
5. For EVERY suggestion you must explain:
   - What changed?
   - Why?
   - Which JD requirement does it address?
   - What original CV evidence justifies this change?
"""


class _SuggestionItem(BaseModel):
    section: str
    original_text: str
    suggested_text: str
    change_description: str
    reason: str
    jd_requirement: str
    evidence: str
    priority: Priority


class _RewriterResponse(BaseModel):
    suggestions: list[_SuggestionItem] = []


class CVRewriterService:
    """Generates concrete Before/After CV improvements grounded in candidate evidence."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm = llm_provider

    async def generate_suggestions(
        self,
        jd: StructuredJD,
        cv: StructuredCV,
        matches: list[RequirementMatch],
    ) -> list[CVSuggestion]:
        """Generate tailored Before/After rewrite suggestions.

        Args:
            jd: Structured JD.
            cv: Structured CV.
            matches: Matching results.

        Returns:
            List of CVSuggestion items.
        """
        # Focus on items that need improvement (partial match, weak evidence, or strong match needing better visibility)
        target_matches = [
            m for m in matches
            if m.status in {MatchStatus.PARTIAL, MatchStatus.WEAK, MatchStatus.STRONG}
            and m.priority != Priority.ALREADY_STRONG
        ]

        if not target_matches:
            target_matches = [m for m in matches if m.status == MatchStatus.PARTIAL][:3]

        if not target_matches:
            # Fallback if already strong everywhere
            return []

        match_contexts = [
            f"- Requirement: {m.requirement} | Status: {m.status.value} | Recommendation: {m.recommendation or ''}"
            for m in target_matches[:5]
        ]

        prompt = f"""Generate up to 5 concrete Before/After rewrite suggestions for this candidate's CV.

CANDIDATE CV ORIGINAL EXCERPTS:
- Summary: {cv.summary or cv.title or 'N/A'}
- Projects: {', '.join(p.name + ': ' + p.description for p in cv.projects[:3]) or 'N/A'}
- Technical Skills: {', '.join(cv.technical_skills[:15]) or 'N/A'}

TARGET JD REQUIREMENTS & GAPS:
{chr(10).join(match_contexts)}

Generate actionable Before/After revisions for the candidate's actual text.
"""

        logger.info("generating_cv_suggestions_started", targets_count=len(target_matches))

        result: _RewriterResponse = await self.llm.generate_structured(
            prompt=prompt,
            response_model=_RewriterResponse,
            system_prompt=CV_REWRITER_SYSTEM_PROMPT,
            temperature=0.2,
        )

        suggestions = [
            CVSuggestion(
                section=s.section,
                original_text=s.original_text,
                suggested_text=s.suggested_text,
                change_description=s.change_description,
                reason=s.reason,
                jd_requirement=s.jd_requirement,
                evidence=s.evidence,
                priority=s.priority,
                accepted=None,
            )
            for s in result.suggestions
        ]

        logger.info("generating_cv_suggestions_completed", suggestions_count=len(suggestions))
        return suggestions
