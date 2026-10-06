"""CV Rewriter service providing Before/After suggestions with strict factual grounding."""

import structlog
from pydantic import BaseModel

from app.domain.enums import MatchStatus, Priority
from app.domain.models import CVSuggestion, RequirementMatch, StructuredCV, StructuredJD
from app.providers.llm.base import LLMProvider

logger = structlog.get_logger()

CV_REWRITER_SYSTEM_PROMPT = """You are an elite Career Coach and Technical Resume Optimization Specialist.
Your task is to analyze the candidate's CV against the Job Description and provide concrete, actionable Before/After rewrite suggestions to maximize CV ↔ JD alignment.

CRITICAL OBJECTIVE:
You must provide between 3 to 6 practical Before/After suggestions covering:
1. Professional Summary / Career Objective: Rewrite to target this specific job title and highlight the candidate's strongest matching strengths.
2. Projects: Enhance project bullet points to explicitly highlight technologies, protocols, and architectural details requested in the JD (e.g. Qt Widgets, signals/slots, Embedded Linux, CAN, etc.) based on existing CV context.
3. Technical Skills Section: Re-order, categorize, and emphasize keywords that match the JD requirements for ATS readability.
4. Experience (if present): Refine duties and achievements to reflect JD responsibilities.

CRITICAL POLICY — NO FABRICATION:
1. The rewritten version MUST remain factually grounded in the candidate's actual background.
2. NEVER invent work history, fake degrees, companies, or tools that have no basis in the CV.
3. If recommending adding a missing requirement (e.g. Docker), you must frame it clearly: "Chỉ bổ sung nếu bạn thực tế đã từng dùng qua trong bài tập/dự án trường."
4. For EVERY suggestion you MUST explain:
   - What changed? (Thay đổi gì)
   - Why? (Tại sao - liên kết với yêu cầu nào trong JD)
   - Which JD requirement does it address?
   - What original CV evidence justifies this?
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
        """Generate tailored Before/After rewrite suggestions across multiple CV sections.

        Args:
            jd: Structured JD.
            cv: Structured CV.
            matches: Matching results.

        Returns:
            List of CVSuggestion items.
        """
        # Collect key gaps and highlights
        gaps = [
            f"- [{m.priority.value.upper()}] {m.requirement} ({m.status.value}): {m.recommendation or ''}"
            for m in matches
            if m.status in {MatchStatus.MISSING, MatchStatus.WEAK, MatchStatus.PARTIAL}
        ][:6]

        strong = [
            f"- [STRONG] {m.requirement}: CV has evidence in {', '.join(e.source_section for e in m.evidence)}"
            for m in matches
            if m.status == MatchStatus.STRONG
        ][:5]

        # Build clean CV overview
        cv_summary = cv.summary or cv.title or "Fresher Software Engineer"
        cv_projects_str = "\n".join(
            f"Project: {p.name}\n- Tech: {', '.join(p.technologies)}\n- Desc: {p.description}\n- Bullets: {' | '.join(p.highlights)}"
            for p in cv.projects
        ) if cv.projects else "N/A"

        cv_skills_str = ", ".join(cv.technical_skills) if cv.technical_skills else "N/A"
        cv_exp_str = "\n".join(
            f"Exp: {w.title} at {w.company} - {w.description}"
            for w in cv.experience
        ) if cv.experience else "N/A"

        prompt = f"""Target Position: {jd.job_title} at {jd.company or 'Target Company'}

KEY JD REQUIREMENTS & GAPS:
{chr(10).join(gaps) if gaps else 'All direct requirements are covered, optimize keyword depth and layout.'}

STRONG MATCHES TO HIGHLIGHT:
{chr(10).join(strong) if strong else 'N/A'}

CANDIDATE ORIGINAL CV CONTENT:
=== SUMMARY / TITLE ===
{cv_summary}

=== TECHNICAL SKILLS ===
{cv_skills_str}

=== PROJECTS ===
{cv_projects_str}

=== EXPERIENCE ===
{cv_exp_str}

TASK:
Provide 3 to 6 high-impact Before/After rewrite suggestions to optimize this CV for '{jd.job_title}'.
Ensure every suggestion provides concrete, ready-to-copy text and clear explanations.
"""

        logger.info("generating_cv_suggestions_started", candidate=cv.name, target_job=jd.job_title)

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
