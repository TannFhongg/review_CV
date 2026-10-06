"""Core domain models."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import MatchStatus, Priority, Importance, SkillCategory


# === JD Models ===

class SkillRequirement(BaseModel):
    """A skill requirement extracted from a Job Description."""
    name: str
    category: SkillCategory
    importance: Importance
    context: str | None = None
    keywords: list[str] = []


class StructuredJD(BaseModel):
    """Structured representation of a Job Description."""
    job_title: str
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    seniority_level: str | None = None

    required_skills: list[SkillRequirement] = []
    preferred_skills: list[SkillRequirement] = []
    responsibilities: list[str] = []

    education_requirements: list[str] = []
    experience_requirements: list[str] = []
    technical_requirements: list[str] = []
    soft_skills: list[str] = []
    language_requirements: list[str] = []
    domain_knowledge: list[str] = []
    tools: list[str] = []

    keywords: list[str] = []
    raw_text: str


# === CV Models ===

class ContactInfo(BaseModel):
    """Contact information from a CV."""
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    website: str | None = None
    location: str | None = None


class Education(BaseModel):
    """Education entry from a CV."""
    institution: str
    degree: str
    field: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    gpa: str | None = None
    details: list[str] = []


class WorkExperience(BaseModel):
    """Work experience entry from a CV."""
    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    description: str = ""
    responsibilities: list[str] = []
    technologies: list[str] = []
    achievements: list[str] = []


class Project(BaseModel):
    """Project entry from a CV."""
    name: str
    description: str = ""
    technologies: list[str] = []
    role: str | None = None
    highlights: list[str] = []
    url: str | None = None


class StructuredCV(BaseModel):
    """Structured representation of a CV."""
    name: str
    title: str | None = None
    summary: str | None = None
    contact: ContactInfo = ContactInfo()

    education: list[Education] = []
    experience: list[WorkExperience] = []
    projects: list[Project] = []

    technical_skills: list[str] = []
    soft_skills: list[str] = []
    certifications: list[str] = []
    languages: list[str] = []
    achievements: list[str] = []

    raw_text: str


# === Match Models ===

class EvidenceItem(BaseModel):
    """Evidence from a CV that supports a JD requirement."""
    source_section: str
    source_text: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    explanation: str


class RequirementMatch(BaseModel):
    """Match result for a single JD requirement against CV evidence."""
    requirement: str
    requirement_importance: Importance
    status: MatchStatus
    evidence: list[EvidenceItem] = []
    recommendation: str | None = None
    priority: Priority = Priority.NICE_TO_HAVE
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class AlignmentScore(BaseModel):
    """Transparent alignment score with methodology documentation."""
    overall: int = Field(ge=0, le=100)
    technical_skills: int = Field(ge=0, le=100)
    experience_relevance: int = Field(ge=0, le=100)
    responsibilities_alignment: int = Field(ge=0, le=100)
    keyword_coverage: int = Field(ge=0, le=100)
    education_alignment: int = Field(ge=0, le=100)
    cv_clarity: int = Field(ge=0, le=100)
    methodology_notes: str


class CVSuggestion(BaseModel):
    """A single CV rewrite suggestion with Before/After and explanation."""
    section: str
    original_text: str
    suggested_text: str
    change_description: str
    reason: str
    jd_requirement: str
    evidence: str
    priority: Priority
    accepted: bool | None = None


class AnalysisResult(BaseModel):
    """Complete analysis result from the pipeline."""
    # Parsed inputs
    structured_jd: StructuredJD
    structured_cv: StructuredCV

    # Matching results
    matches: list[RequirementMatch]

    # Scores
    alignment_score: AlignmentScore

    # Recommendations
    top_recommendations: list[RequirementMatch]
    suggestions: list[CVSuggestion]

    # Summary counts
    strong_count: int
    partial_count: int
    weak_count: int
    missing_count: int

    # Metadata
    analyzed_at: datetime
    processing_time_seconds: float
