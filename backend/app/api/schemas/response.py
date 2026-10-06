"""Response schemas for the API."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import MatchStatus, Priority, Importance, SkillCategory


# === JD Models ===

class SkillRequirementResponse(BaseModel):
    """A skill requirement from the JD."""
    name: str
    category: SkillCategory
    importance: Importance
    context: str | None = None
    keywords: list[str] = []


class StructuredJDResponse(BaseModel):
    """Structured representation of a Job Description."""
    job_title: str
    company: str | None = None
    location: str | None = None
    employment_type: str | None = None
    seniority_level: str | None = None
    required_skills: list[SkillRequirementResponse] = []
    preferred_skills: list[SkillRequirementResponse] = []
    responsibilities: list[str] = []
    education_requirements: list[str] = []
    experience_requirements: list[str] = []
    technical_requirements: list[str] = []
    soft_skills: list[str] = []
    language_requirements: list[str] = []
    domain_knowledge: list[str] = []
    tools: list[str] = []
    keywords: list[str] = []


# === CV Models ===

class ContactInfoResponse(BaseModel):
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    website: str | None = None
    location: str | None = None


class EducationResponse(BaseModel):
    institution: str
    degree: str
    field: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    gpa: str | None = None
    details: list[str] = []


class WorkExperienceResponse(BaseModel):
    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    description: str = ""
    responsibilities: list[str] = []
    technologies: list[str] = []
    achievements: list[str] = []


class ProjectResponse(BaseModel):
    name: str
    description: str = ""
    technologies: list[str] = []
    role: str | None = None
    highlights: list[str] = []
    url: str | None = None


class StructuredCVResponse(BaseModel):
    """Structured representation of a CV."""
    name: str
    title: str | None = None
    summary: str | None = None
    contact: ContactInfoResponse = ContactInfoResponse()
    education: list[EducationResponse] = []
    experience: list[WorkExperienceResponse] = []
    projects: list[ProjectResponse] = []
    technical_skills: list[str] = []
    soft_skills: list[str] = []
    certifications: list[str] = []
    languages: list[str] = []
    achievements: list[str] = []


# === Match Models ===

class EvidenceItemResponse(BaseModel):
    """Evidence from CV for a JD requirement."""
    source_section: str
    source_text: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    explanation: str


class RequirementMatchResponse(BaseModel):
    """Match result for a JD requirement."""
    requirement: str
    requirement_importance: Importance
    status: MatchStatus
    evidence: list[EvidenceItemResponse] = []
    recommendation: str | None = None
    priority: Priority = Priority.NICE_TO_HAVE
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class AlignmentScoreResponse(BaseModel):
    """Transparent alignment score breakdown."""
    overall: int = Field(ge=0, le=100)
    technical_skills: int = Field(ge=0, le=100)
    experience_relevance: int = Field(ge=0, le=100)
    responsibilities_alignment: int = Field(ge=0, le=100)
    keyword_coverage: int = Field(ge=0, le=100)
    education_alignment: int = Field(ge=0, le=100)
    cv_clarity: int = Field(ge=0, le=100)
    methodology_notes: str


class CVSuggestionResponse(BaseModel):
    """A CV rewrite suggestion with Before/After."""
    section: str
    original_text: str
    suggested_text: str
    change_description: str
    reason: str
    jd_requirement: str
    evidence: str
    priority: Priority
    accepted: bool | None = None


# === Main Response ===

class AnalysisResponse(BaseModel):
    """Complete analysis result."""
    structured_jd: StructuredJDResponse
    structured_cv: StructuredCVResponse
    matches: list[RequirementMatchResponse]
    alignment_score: AlignmentScoreResponse
    top_recommendations: list[RequirementMatchResponse]
    suggestions: list[CVSuggestionResponse]
    strong_count: int
    partial_count: int
    weak_count: int
    missing_count: int
    analyzed_at: datetime
    processing_time_seconds: float


# === Error Response ===

class ErrorDetail(BaseModel):
    """Error detail."""
    code: str
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: ErrorDetail


# === Cover Letter Response ===

class CoverLetterResponse(BaseModel):
    """Generated Cover Letter response."""
    subject: str
    salutation: str
    opening: str
    body_paragraphs: list[str]
    closing: str
    sign_off: str
    full_letter: str
    tone: str
    language: str
    word_count: int
    key_strengths_highlighted: list[str] = []

