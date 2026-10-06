"""Matching Engine for semantic JD ↔ CV comparison and evidence mapping."""

import structlog
from pydantic import BaseModel, Field

from app.domain.enums import Importance, MatchStatus, Priority
from app.domain.models import (
    EvidenceItem,
    RequirementMatch,
    StructuredCV,
    StructuredJD,
)
from app.providers.llm.base import LLMProvider

logger = structlog.get_logger()

# Common technical aliases and synonyms
SKILL_ALIASES: dict[str, list[str]] = {
    "c++": ["cpp", "c/c++", "c plus plus", "modern c++"],
    "c": ["c language", "ansi c", "embedded c"],
    "python": ["py", "python3"],
    "javascript": ["js", "es6", "ecmascript"],
    "typescript": ["ts"],
    "qt": ["qt widgets", "qt quick", "qml", "qt creator", "qt5", "qt6"],
    "linux": ["embedded linux", "ubuntu", "debian", "posix", "yocto", "unix"],
    "freertos": ["rtos", "real-time os"],
    "can": ["can bus", "can protocol", "can-bus", "controller area network"],
    "docker": ["container", "containers", "dockerfile", "containerization"],
    "kubernetes": ["k8s"],
    "git": ["github", "gitlab", "bitbucket", "version control"],
}

MATCHING_SYSTEM_PROMPT = """You are an elite Technical Hiring Manager and Senior Recruiter.
Your task is to analyze candidate CV evidence against specific Job Description (JD) requirements.

CRITICAL POLICY — EVIDENCE FIRST & NO FABRICATION:
1. ONLY use evidence explicitly present in the candidate's CV text.
2. NEVER invent experience, skills, projects, metrics, or achievements.
3. If a requirement is NOT found in the CV, you MUST return:
   - status: "missing"
   - evidence: []
   - recommendation: "Not found in CV. Potential improvement — only add this if you genuinely have this experience."
4. Match status classifications:
   - "strong_match": Candidate has direct, explicit, hands-on proof matching the requirement.
   - "partial_match": Candidate has relevant experience or related technology, but lacks full depth or explicit mention.
   - "weak_evidence": Minor mention or adjacent technology (e.g., JD asks for Linux, CV only mentions Raspberry Pi without mentioning Linux).
   - "missing": No evidence in CV whatsoever.
5. Recommendation guidelines:
   - Explain WHY based on CV evidence.
   - Suggest concrete CV optimizations (e.g. "Move this project higher", "Explicitly mention Qt Widgets and signal/slot").
   - Do NOT just say "You should add X".
"""


class _EvidenceItemExtraction(BaseModel):
    source_section: str
    source_text: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    explanation: str


class _RequirementMatchExtraction(BaseModel):
    requirement: str
    status: MatchStatus
    evidence: list[_EvidenceItemExtraction] = []
    recommendation: str
    confidence: float = Field(ge=0.0, le=1.0)


class _BatchMatchResponse(BaseModel):
    matches: list[_RequirementMatchExtraction]


class MatchingEngine:
    """Matches JD requirements against CV content with semantic evidence mapping."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm = llm_provider

    def _build_cv_summary(self, cv: StructuredCV) -> str:
        """Create a clear textual summary of all sections of the CV for the LLM."""
        sections: list[str] = []

        if cv.title or cv.summary:
            sections.append(f"TITLE/SUMMARY:\n{cv.title or ''} - {cv.summary or ''}")

        if cv.technical_skills:
            sections.append(f"TECHNICAL SKILLS:\n{', '.join(cv.technical_skills)}")

        if cv.projects:
            proj_texts: list[str] = []
            for p in cv.projects:
                techs = f" (Tech: {', '.join(p.technologies)})" if p.technologies else ""
                highlights = " | ".join(p.highlights) if p.highlights else ""
                proj_texts.append(f"- Project '{p.name}'{techs}: {p.description} {highlights}".strip())
            sections.append("PROJECTS:\n" + "\n".join(proj_texts))

        if cv.experience:
            exp_texts: list[str] = []
            for e in cv.experience:
                techs = f" (Tech: {', '.join(e.technologies)})" if e.technologies else ""
                duties = " | ".join(e.responsibilities) if e.responsibilities else ""
                exp_texts.append(f"- {e.title} at {e.company}{techs}: {e.description} {duties}".strip())
            sections.append("WORK EXPERIENCE:\n" + "\n".join(exp_texts))

        if cv.education:
            edu_texts = [
                f"- {e.degree} in {e.field or 'Engineering'} at {e.institution}"
                for e in cv.education
            ]
            sections.append("EDUCATION:\n" + "\n".join(edu_texts))

        if cv.certifications:
            sections.append(f"CERTIFICATIONS:\n{', '.join(cv.certifications)}")

        if cv.languages:
            sections.append(f"LANGUAGES:\n{', '.join(cv.languages)}")

        return "\n\n".join(sections)

    def _determine_priority(self, importance: Importance, status: MatchStatus) -> Priority:
        """Calculate recommendation priority according to standard rules."""
        if status == MatchStatus.STRONG:
            return Priority.ALREADY_STRONG
        if importance == Importance.REQUIRED:
            if status == MatchStatus.MISSING or status == MatchStatus.WEAK:
                return Priority.MUST_FIX
            return Priority.SHOULD_FIX
        elif importance == Importance.PREFERRED:
            if status == MatchStatus.MISSING or status == MatchStatus.WEAK:
                return Priority.SHOULD_FIX
            return Priority.NICE_TO_HAVE
        return Priority.NICE_TO_HAVE

    async def match(self, jd: StructuredJD, cv: StructuredCV) -> list[RequirementMatch]:
        """Perform semantic matching of JD requirements against CV content.

        Args:
            jd: Structured Job Description.
            cv: Structured CV.

        Returns:
            List of RequirementMatch items with evidence and recommendations.
        """
        requirements_to_check: list[tuple[str, Importance]] = []

        # 1. Required skills
        for skill in jd.required_skills:
            requirements_to_check.append((skill.name, Importance.REQUIRED))

        # 2. Preferred skills
        for skill in jd.preferred_skills:
            requirements_to_check.append((skill.name, Importance.PREFERRED))

        # 3. Additional technical requirements
        for req in jd.technical_requirements:
            if not any(req.lower() == r[0].lower() for r in requirements_to_check):
                requirements_to_check.append((req, Importance.REQUIRED))

        # 4. Key responsibilities (up to 3 key responsibilities)
        for resp in jd.responsibilities[:3]:
            requirements_to_check.append((f"Responsibility: {resp}", Importance.REQUIRED))

        if not requirements_to_check:
            # Fallback if JD had minimal structured items
            requirements_to_check.append((jd.job_title, Importance.REQUIRED))

        cv_summary = self._build_cv_summary(cv)

        req_list_str = "\n".join(
            f"{i+1}. [{imp.value.upper()}] {req}"
            for i, (req, imp) in enumerate(requirements_to_check)
        )

        prompt = f"""Compare the following JD requirements against the candidate's CV.
For each requirement, evaluate match status, identify exact evidence from the CV, and provide actionable recommendations.

JD REQUIREMENTS TO EVALUATE:
{req_list_str}

CANDIDATE CV CONTENT:
\"\"\"
{cv_summary}
\"\"\"
"""

        logger.info(
            "matching_started",
            requirements_count=len(requirements_to_check),
            candidate_name=cv.name,
        )

        batch_result: _BatchMatchResponse = await self.llm.generate_structured(
            prompt=prompt,
            response_model=_BatchMatchResponse,
            system_prompt=MATCHING_SYSTEM_PROMPT,
            temperature=0.1,
        )

        # Merge results with our priority rules
        final_matches: list[RequirementMatch] = []
        extracted_map = {m.requirement.lower().strip(): m for m in batch_result.matches}

        for req_name, importance in requirements_to_check:
            clean_name = req_name.lower().strip()
            # Find closest match or direct match
            found = extracted_map.get(clean_name)
            if not found:
                # Partial key search
                for key, val in extracted_map.items():
                    if clean_name in key or key in clean_name:
                        found = val
                        break

            if found:
                status = found.status
                evidence_items = [
                    EvidenceItem(
                        source_section=e.source_section,
                        source_text=e.source_text,
                        relevance_score=e.relevance_score,
                        explanation=e.explanation,
                    )
                    for e in found.evidence
                ]
                rec = found.recommendation
                conf = found.confidence
            else:
                status = MatchStatus.UNKNOWN
                evidence_items = []
                rec = "Không đủ dữ liệu để phân tích."
                conf = 0.0

            priority = self._determine_priority(importance, status)

            final_matches.append(
                RequirementMatch(
                    requirement=req_name,
                    requirement_importance=importance,
                    status=status,
                    evidence=evidence_items,
                    recommendation=rec,
                    priority=priority,
                    confidence=conf,
                )
            )

        logger.info("matching_completed", total_matches=len(final_matches))
        return final_matches
