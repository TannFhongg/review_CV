"""Service for extracting structured data from Job Descriptions (JD)."""

import structlog
from pydantic import BaseModel

from app.domain.enums import Importance, SkillCategory
from app.domain.models import SkillRequirement, StructuredJD
from app.providers.llm.base import LLMProvider

logger = structlog.get_logger()

JD_PARSER_SYSTEM_PROMPT = """You are an elite Technical Recruiter and HR Systems Architect.
Your task is to analyze a Job Description (JD) in Vietnamese or English and convert it into a strictly structured representation.

CRITICAL RULES:
1. NO FABRICATION: Only extract requirements, skills, and details actually mentioned or strongly requested in the JD.
2. CATEGORIZATION:
   - Differentiate strictly between 'required' (must have) and 'preferred' (nice to have / bonus) skills.
   - If the JD says "Yêu cầu", "Requirements", "Must have", mark importance as "required".
   - If the JD says "Ưu tiên", "Plus", "Preferred", "Nice to have", mark importance as "preferred".
3. COMPREHENSIVE SKILL BREAKDOWN:
   - Break composite skills down (e.g. "C++/Qt on Linux" -> "C++", "Qt", "Linux").
   - Extract relevant keywords and aliases for each skill.
4. RESPONSIBILITIES: Extract actionable duty bullet points cleanly.
5. PRESERVE ORIGINAL INTENT: Do not over-generalize or omit crucial technical specifications.
"""


class _SkillExtraction(BaseModel):
    name: str
    category: SkillCategory
    importance: Importance
    context: str | None = None
    keywords: list[str] = []


class _JDExtractionResponse(BaseModel):
    job_title: str
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    seniority_level: str | None = None
    required_skills: list[_SkillExtraction] = []
    preferred_skills: list[_SkillExtraction] = []
    responsibilities: list[str] = []
    education_requirements: list[str] = []
    experience_requirements: list[str] = []
    technical_requirements: list[str] = []
    soft_skills: list[str] = []
    language_requirements: list[str] = []
    domain_knowledge: list[str] = []
    tools: list[str] = []
    keywords: list[str] = []


class JDParserService:
    """Parses raw JD text into StructuredJD domain model."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm = llm_provider

    async def parse(self, raw_text: str) -> StructuredJD:
        """Parse raw JD text into StructuredJD.

        Args:
            raw_text: Raw plain text of the Job Description.

        Returns:
            StructuredJD object.

        Raises:
            ValueError: If text is empty.
        """
        if not raw_text or not raw_text.strip():
            raise ValueError("Văn bản Job Description không được để trống.")

        logger.info("parsing_jd_started", text_length=len(raw_text))

        prompt = f"""Extract the following Job Description into a structured schema:

JOB DESCRIPTION:
\"\"\"
{raw_text}
\"\"\"
"""

        result: _JDExtractionResponse = await self.llm.generate_structured(
            prompt=prompt,
            response_model=_JDExtractionResponse,
            system_prompt=JD_PARSER_SYSTEM_PROMPT,
            temperature=0.1,
        )

        structured_jd = StructuredJD(
            job_title=result.job_title,
            company=result.company,
            location=result.location,
            employment_type=result.employment_type,
            seniority_level=result.seniority_level,
            required_skills=[
                SkillRequirement(
                    name=s.name,
                    category=s.category,
                    importance=s.importance,
                    context=s.context,
                    keywords=s.keywords,
                )
                for s in result.required_skills
            ],
            preferred_skills=[
                SkillRequirement(
                    name=s.name,
                    category=s.category,
                    importance=s.importance,
                    context=s.context,
                    keywords=s.keywords,
                )
                for s in result.preferred_skills
            ],
            responsibilities=result.responsibilities,
            education_requirements=result.education_requirements,
            experience_requirements=result.experience_requirements,
            technical_requirements=result.technical_requirements,
            soft_skills=result.soft_skills,
            language_requirements=result.language_requirements,
            domain_knowledge=result.domain_knowledge,
            tools=result.tools,
            keywords=result.keywords,
            raw_text=raw_text,
        )

        logger.info(
            "parsing_jd_completed",
            job_title=structured_jd.job_title,
            required_count=len(structured_jd.required_skills),
            preferred_count=len(structured_jd.preferred_skills),
        )

        return structured_jd
