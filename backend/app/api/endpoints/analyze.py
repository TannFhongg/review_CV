"""Analysis endpoint — main CV analysis pipeline implementation."""

from typing import Annotated
from pathlib import Path

import structlog
from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from app.api.schemas.request import validate_analysis_input
from app.api.schemas.response import (
    AlignmentScoreResponse,
    AnalysisResponse,
    CVSuggestionResponse,
    ErrorResponse,
    EvidenceItemResponse,
    RequirementMatchResponse,
    SkillRequirementResponse,
    StructuredCVResponse,
    StructuredJDResponse,
    ContactInfoResponse,
    EducationResponse,
    WorkExperienceResponse,
    ProjectResponse,
)
from app.services.pipeline import AnalysisPipeline
from app.services.report_generator import ReportGenerator
from app.utils.file_utils import cleanup_temp_file, save_temp_file

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Phân tích CV so với Job Description",
    description=(
        "Upload JD và CV (file hoặc text), hệ thống sẽ phân tích alignment, "
        "tìm gaps, và đưa ra gợi ý tối ưu dựa trên bằng chứng thực tế."
    ),
)
async def analyze(
    jd_file: Annotated[UploadFile | None, File(description="Job Description file (PDF/DOCX/TXT)")] = None,
    cv_file: Annotated[UploadFile | None, File(description="CV file (PDF/DOCX/TXT)")] = None,
    jd_text: Annotated[str | None, Form(description="Job Description as plain text")] = None,
    cv_text: Annotated[str | None, Form(description="CV as plain text")] = None,
) -> AnalysisResponse:
    """Analyze a CV against a Job Description.

    Accepts either file uploads or plain text for both JD and CV.
    Guarantees privacy by cleaning up all temporary files immediately.
    """
    # 1. Validate inputs
    validate_analysis_input(jd_file, cv_file, jd_text, cv_text)

    temp_jd_path: str | None = None
    temp_cv_path: str | None = None

    try:
        # Save temp files if uploaded
        if jd_file and jd_file.filename:
            ext = Path(jd_file.filename).suffix.lower()
            content = await jd_file.read()
            temp_jd_path = await save_temp_file(content, ext)

        if cv_file and cv_file.filename:
            ext = Path(cv_file.filename).suffix.lower()
            content = await cv_file.read()
            temp_cv_path = await save_temp_file(content, ext)

        # Execute full analysis pipeline
        pipeline = AnalysisPipeline()
        result = await pipeline.run(
            jd_text=jd_text,
            cv_text=cv_text,
            jd_file_path=temp_jd_path,
            cv_file_path=temp_cv_path,
        )

        # Convert domain model to response schema
        response = AnalysisResponse(
            structured_jd=StructuredJDResponse(
                job_title=result.structured_jd.job_title,
                company=result.structured_jd.company,
                location=result.structured_jd.location,
                employment_type=result.structured_jd.employment_type,
                seniority_level=result.structured_jd.seniority_level,
                required_skills=[
                    SkillRequirementResponse(
                        name=s.name,
                        category=s.category,
                        importance=s.importance,
                        context=s.context,
                        keywords=s.keywords,
                    )
                    for s in result.structured_jd.required_skills
                ],
                preferred_skills=[
                    SkillRequirementResponse(
                        name=s.name,
                        category=s.category,
                        importance=s.importance,
                        context=s.context,
                        keywords=s.keywords,
                    )
                    for s in result.structured_jd.preferred_skills
                ],
                responsibilities=result.structured_jd.responsibilities,
                education_requirements=result.structured_jd.education_requirements,
                experience_requirements=result.structured_jd.experience_requirements,
                technical_requirements=result.structured_jd.technical_requirements,
                soft_skills=result.structured_jd.soft_skills,
                language_requirements=result.structured_jd.language_requirements,
                domain_knowledge=result.structured_jd.domain_knowledge,
                tools=result.structured_jd.tools,
                keywords=result.structured_jd.keywords,
            ),
            structured_cv=StructuredCVResponse(
                name=result.structured_cv.name,
                title=result.structured_cv.title,
                summary=result.structured_cv.summary,
                contact=ContactInfoResponse(
                    email=result.structured_cv.contact.email,
                    phone=result.structured_cv.contact.phone,
                    linkedin=result.structured_cv.contact.linkedin,
                    github=result.structured_cv.contact.github,
                    website=result.structured_cv.contact.website,
                    location=result.structured_cv.contact.location,
                ),
                education=[
                    EducationResponse(
                        institution=e.institution,
                        degree=e.degree,
                        field=e.field,
                        start_date=e.start_date,
                        end_date=e.end_date,
                        gpa=e.gpa,
                        details=e.details,
                    )
                    for e in result.structured_cv.education
                ],
                experience=[
                    WorkExperienceResponse(
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
                    for w in result.structured_cv.experience
                ],
                projects=[
                    ProjectResponse(
                        name=p.name,
                        description=p.description,
                        technologies=p.technologies,
                        role=p.role,
                        highlights=p.highlights,
                        url=p.url,
                    )
                    for p in result.structured_cv.projects
                ],
                technical_skills=result.structured_cv.technical_skills,
                soft_skills=result.structured_cv.soft_skills,
                certifications=result.structured_cv.certifications,
                languages=result.structured_cv.languages,
                achievements=result.structured_cv.achievements,
            ),
            matches=[
                RequirementMatchResponse(
                    requirement=m.requirement,
                    requirement_importance=m.requirement_importance,
                    status=m.status,
                    evidence=[
                        EvidenceItemResponse(
                            source_section=e.source_section,
                            source_text=e.source_text,
                            relevance_score=e.relevance_score,
                            explanation=e.explanation,
                        )
                        for e in m.evidence
                    ],
                    recommendation=m.recommendation,
                    priority=m.priority,
                    confidence=m.confidence,
                )
                for m in result.matches
            ],
            alignment_score=AlignmentScoreResponse(
                overall=result.alignment_score.overall,
                technical_skills=result.alignment_score.technical_skills,
                experience_relevance=result.alignment_score.experience_relevance,
                responsibilities_alignment=result.alignment_score.responsibilities_alignment,
                keyword_coverage=result.alignment_score.keyword_coverage,
                education_alignment=result.alignment_score.education_alignment,
                cv_clarity=result.alignment_score.cv_clarity,
                methodology_notes=result.alignment_score.methodology_notes,
            ),
            top_recommendations=[
                RequirementMatchResponse(
                    requirement=m.requirement,
                    requirement_importance=m.requirement_importance,
                    status=m.status,
                    evidence=[
                        EvidenceItemResponse(
                            source_section=e.source_section,
                            source_text=e.source_text,
                            relevance_score=e.relevance_score,
                            explanation=e.explanation,
                        )
                        for e in m.evidence
                    ],
                    recommendation=m.recommendation,
                    priority=m.priority,
                    confidence=m.confidence,
                )
                for m in result.top_recommendations
            ],
            suggestions=[
                CVSuggestionResponse(
                    section=s.section,
                    original_text=s.original_text,
                    suggested_text=s.suggested_text,
                    change_description=s.change_description,
                    reason=s.reason,
                    jd_requirement=s.jd_requirement,
                    evidence=s.evidence,
                    priority=s.priority,
                    accepted=s.accepted,
                )
                for s in result.suggestions
            ],
            strong_count=result.strong_count,
            partial_count=result.partial_count,
            weak_count=result.weak_count,
            missing_count=result.missing_count,
            analyzed_at=result.analyzed_at,
            processing_time_seconds=result.processing_time_seconds,
        )

        return response

    except ValueError as e:
        logger.warning("analyze_input_value_error", error=str(e))
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_INPUT", "message": str(e)},
        ) from e
    except Exception as e:
        logger.error("analyze_pipeline_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"code": "PROCESSING_ERROR", "message": f"Lỗi trong quá trình phân tích: {e}"},
        ) from e
    finally:
        # Guarantee privacy by cleaning up all temp files
        if temp_jd_path:
            cleanup_temp_file(temp_jd_path)
        if temp_cv_path:
            cleanup_temp_file(temp_cv_path)


@router.post(
    "/report/markdown",
    summary="Tạo báo cáo Markdown từ kết quả phân tích",
    description="Chuyển đổi kết quả phân tích thành báo cáo chi tiết định dạng Markdown để tải về hoặc xem trước.",
)
async def generate_markdown_report(data: AnalysisResponse) -> dict[str, str]:
    """Generate markdown report string from an analysis response."""
    # Convert response back to domain models for report generation
    from app.domain.models import (
        AlignmentScore,
        AnalysisResult,
        CVSuggestion,
        EvidenceItem,
        RequirementMatch,
        StructuredCV,
        StructuredJD,
    )

    domain_jd = StructuredJD(
        job_title=data.structured_jd.job_title,
        company=data.structured_jd.company,
        raw_text="",
    )
    domain_cv = StructuredCV(
        name=data.structured_cv.name,
        raw_text="",
    )
    domain_matches = [
        RequirementMatch(
            requirement=m.requirement,
            requirement_importance=m.requirement_importance,
            status=m.status,
            evidence=[
                EvidenceItem(
                    source_section=e.source_section,
                    source_text=e.source_text,
                    relevance_score=e.relevance_score,
                    explanation=e.explanation,
                )
                for e in m.evidence
            ],
            recommendation=m.recommendation,
            priority=m.priority,
            confidence=m.confidence,
        )
        for m in data.matches
    ]
    domain_top = [
        RequirementMatch(
            requirement=m.requirement,
            requirement_importance=m.requirement_importance,
            status=m.status,
            evidence=[
                EvidenceItem(
                    source_section=e.source_section,
                    source_text=e.source_text,
                    relevance_score=e.relevance_score,
                    explanation=e.explanation,
                )
                for e in m.evidence
            ],
            recommendation=m.recommendation,
            priority=m.priority,
            confidence=m.confidence,
        )
        for m in data.top_recommendations
    ]
    domain_suggestions = [
        CVSuggestion(
            section=s.section,
            original_text=s.original_text,
            suggested_text=s.suggested_text,
            change_description=s.change_description,
            reason=s.reason,
            jd_requirement=s.jd_requirement,
            evidence=s.evidence,
            priority=s.priority,
        )
        for s in data.suggestions
    ]
    domain_score = AlignmentScore(
        overall=data.alignment_score.overall,
        technical_skills=data.alignment_score.technical_skills,
        experience_relevance=data.alignment_score.experience_relevance,
        responsibilities_alignment=data.alignment_score.responsibilities_alignment,
        keyword_coverage=data.alignment_score.keyword_coverage,
        education_alignment=data.alignment_score.education_alignment,
        cv_clarity=data.alignment_score.cv_clarity,
        methodology_notes=data.alignment_score.methodology_notes,
    )

    domain_result = AnalysisResult(
        structured_jd=domain_jd,
        structured_cv=domain_cv,
        matches=domain_matches,
        alignment_score=domain_score,
        top_recommendations=domain_top,
        suggestions=domain_suggestions,
        strong_count=data.strong_count,
        partial_count=data.partial_count,
        weak_count=data.weak_count,
        missing_count=data.missing_count,
        analyzed_at=data.analyzed_at,
        processing_time_seconds=data.processing_time_seconds,
    )

    markdown = ReportGenerator.generate_markdown(domain_result)
    return {"markdown": markdown}
