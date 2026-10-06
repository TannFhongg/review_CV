"""Service for extracting structured data from candidate CV / Resumes."""

import structlog
from pydantic import BaseModel

from app.domain.models import (
    ContactInfo,
    Education,
    Project,
    StructuredCV,
    WorkExperience,
)
from app.providers.llm.base import LLMProvider

logger = structlog.get_logger()

CV_PARSER_SYSTEM_PROMPT = """You are an expert Technical Resume Analyst and Parser.
Your task is to parse a candidate's CV/Resume in Vietnamese or English into a structured representation.

CRITICAL POLICY - NO FABRICATION:
1. NEVER invent or assume any work experience, company, project, technology, certification, metric, GPA, or date.
2. If a section is missing from the CV (e.g. no certifications or no experience), leave that list empty.
3. Extract exact technical skills and libraries mentioned (e.g. C++, Qt Widgets, FreeRTOS, CAN, Linux).
4. Preserve candidate's exact project descriptions, highlights, and bullet points accurately.
5. If the candidate is a fresher or student with academic projects instead of corporate experience, capture those projects under 'projects'.
"""


class _EducationExtraction(BaseModel):
    institution: str
    degree: str
    field: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    gpa: str | None = None
    details: list[str] = []


class _WorkExperienceExtraction(BaseModel):
    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    description: str = ""
    responsibilities: list[str] = []
    technologies: list[str] = []
    achievements: list[str] = []


class _ProjectExtraction(BaseModel):
    name: str
    description: str = ""
    technologies: list[str] = []
    role: str | None = None
    highlights: list[str] = []
    url: str | None = None


class _ContactExtraction(BaseModel):
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    website: str | None = None
    location: str | None = None


class _CVExtractionResponse(BaseModel):
    name: str
    title: str | None = None
    summary: str | None = None
    contact: _ContactExtraction = _ContactExtraction()
    education: list[_EducationExtraction] = []
    experience: list[_WorkExperienceExtraction] = []
    projects: list[_ProjectExtraction] = []
    technical_skills: list[str] = []
    soft_skills: list[str] = []
    certifications: list[str] = []
    languages: list[str] = []
    achievements: list[str] = []


class CVParserService:
    """Parses raw CV text into StructuredCV domain model."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm = llm_provider

    async def parse(self, raw_text: str) -> StructuredCV:
        """Parse raw CV text into StructuredCV.

        Args:
            raw_text: Raw plain text of the CV.

        Returns:
            StructuredCV object.

        Raises:
            ValueError: If text is empty.
        """
        if not raw_text or not raw_text.strip():
            raise ValueError("Văn bản CV không được để trống.")

        logger.info("parsing_cv_started", text_length=len(raw_text))

        prompt = f"""Extract the following CV / Resume into the structured schema:

CV CONTENT:
\"\"\"
{raw_text}
\"\"\"
"""

        result: _CVExtractionResponse = await self.llm.generate_structured(
            prompt=prompt,
            response_model=_CVExtractionResponse,
            system_prompt=CV_PARSER_SYSTEM_PROMPT,
            temperature=0.1,
        )

        structured_cv = StructuredCV(
            name=result.name,
            title=result.title,
            summary=result.summary,
            contact=ContactInfo(
                email=result.contact.email,
                phone=result.contact.phone,
                linkedin=result.contact.linkedin,
                github=result.contact.github,
                website=result.contact.website,
                location=result.contact.location,
            ),
            education=[
                Education(
                    institution=e.institution,
                    degree=e.degree,
                    field=e.field,
                    start_date=e.start_date,
                    end_date=e.end_date,
                    gpa=e.gpa,
                    details=e.details,
                )
                for e in result.education
            ],
            experience=[
                WorkExperience(
                    company=w.company,
                    title=w.title,
                    start_date=w.start_date,
                    end_date=w.end_date,
                    is_current=w.is_current,
                    description=w.description,
                    responsibilities=w.responsibilities,
                    technologies=w.technologies,
                    achievements=w.achievements,
                )
                for w in result.experience
            ],
            projects=[
                Project(
                    name=p.name,
                    description=p.description,
                    technologies=p.technologies,
                    role=p.role,
                    highlights=p.highlights,
                    url=p.url,
                )
                for p in result.projects
            ],
            technical_skills=result.technical_skills,
            soft_skills=result.soft_skills,
            certifications=result.certifications,
            languages=result.languages,
            achievements=result.achievements,
            raw_text=raw_text,
        )

        logger.info(
            "parsing_cv_completed",
            candidate_name=structured_cv.name,
            projects_count=len(structured_cv.projects),
            skills_count=len(structured_cv.technical_skills),
        )

        return structured_cv
