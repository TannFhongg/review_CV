"""Unit tests for GapAnalyzer, ScoringService, PriorityAnalyzer, and ReportGenerator."""

from datetime import datetime

import pytest

from app.domain.enums import Importance, MatchStatus, Priority, SkillCategory
from app.domain.models import (
    AlignmentScore,
    AnalysisResult,
    CVSuggestion,
    Education,
    EvidenceItem,
    Project,
    RequirementMatch,
    SkillRequirement,
    StructuredCV,
    StructuredJD,
)
from app.services.gap_analyzer import GapAnalyzer
from app.services.priority_analyzer import PriorityAnalyzer
from app.services.report_generator import ReportGenerator
from app.services.scoring import ScoringService


@pytest.fixture
def sample_models():
    jd = StructuredJD(
        job_title="Senior C++ Automotive Engineer",
        company="TechAuto",
        required_skills=[
            SkillRequirement(
                name="C++",
                category=SkillCategory.TECHNICAL,
                importance=Importance.REQUIRED,
                keywords=["C++", "Modern C++"],
            ),
            SkillRequirement(
                name="Qt",
                category=SkillCategory.TECHNICAL,
                importance=Importance.REQUIRED,
                keywords=["Qt"],
            ),
            SkillRequirement(
                name="Docker",
                category=SkillCategory.TOOL,
                importance=Importance.REQUIRED,
                keywords=["Docker"],
            ),
        ],
        preferred_skills=[
            SkillRequirement(
                name="AUTOSAR",
                category=SkillCategory.DOMAIN,
                importance=Importance.PREFERRED,
                keywords=["AUTOSAR"],
            ),
        ],
        keywords=["C++", "Qt", "Docker", "AUTOSAR", "Linux", "CAN"],
        raw_text="Sample JD with C++, Qt, Docker, AUTOSAR, Linux, CAN",
    )

    cv = StructuredCV(
        name="Võ Văn Tuấn",
        title="Fresher C++ Software Engineer",
        summary="C++ developer with passion for embedded automotive systems",
        education=[
            Education(
                institution="HCMUT",
                degree="Bachelor",
                field="Computer Engineering",
            )
        ],
        projects=[
            Project(
                name="VTuber Avatar Control Panel",
                description="Built with C++ and Qt Widgets",
                technologies=["C++", "Qt", "Qt Creator"],
            ),
        ],
        technical_skills=["C++", "Qt", "Linux", "CAN"],
        raw_text="Võ Văn Tuấn C++ Fresher developer with Qt Widgets, Linux, CAN",
    )

    matches = [
        RequirementMatch(
            requirement="C++",
            requirement_importance=Importance.REQUIRED,
            status=MatchStatus.STRONG,
            evidence=[
                EvidenceItem(
                    source_section="skills",
                    source_text="C++",
                    relevance_score=1.0,
                    explanation="Direct match in skills and projects",
                )
            ],
            recommendation="Đã phù hợp tốt.",
            priority=Priority.ALREADY_STRONG,
        ),
        RequirementMatch(
            requirement="Qt",
            requirement_importance=Importance.REQUIRED,
            status=MatchStatus.STRONG,
            evidence=[
                EvidenceItem(
                    source_section="projects",
                    source_text="VTuber Avatar Control Panel (Qt)",
                    relevance_score=0.9,
                    explanation="Developed Qt application",
                )
            ],
            recommendation="Nhấn mạnh Qt Widgets và signal/slot.",
            priority=Priority.ALREADY_STRONG,
        ),
        RequirementMatch(
            requirement="Docker",
            requirement_importance=Importance.REQUIRED,
            status=MatchStatus.MISSING,
            evidence=[],
            recommendation="Not found in CV. Chỉ thêm nếu có kinh nghiệm.",
            priority=Priority.MUST_FIX,
        ),
        RequirementMatch(
            requirement="AUTOSAR",
            requirement_importance=Importance.PREFERRED,
            status=MatchStatus.MISSING,
            evidence=[],
            recommendation="Not found in CV.",
            priority=Priority.SHOULD_FIX,
        ),
    ]

    return jd, cv, matches


# === Gap Analyzer Tests ===

class TestGapAnalyzer:
    def test_summarize_counts(self, sample_models):
        _, _, matches = sample_models
        summary = GapAnalyzer.summarize(matches)

        assert summary.strong_count == 2
        assert summary.missing_count == 2
        assert summary.partial_count == 0
        assert summary.weak_count == 0
        assert summary.must_fix_count == 1
        assert summary.should_fix_count == 1
        assert summary.already_strong_count == 2

    def test_filter_gaps(self, sample_models):
        _, _, matches = sample_models
        gaps = GapAnalyzer.filter_gaps(matches)
        assert len(gaps) == 2
        assert all(g.status == MatchStatus.MISSING for g in gaps)


# === Scoring Service Tests ===

class TestScoringService:
    def test_calculate_technical_score(self, sample_models):
        _, _, matches = sample_models
        score = ScoringService.calculate_technical_skills_score(matches)
        # 2 required strong (3*1 + 3*1 = 6), 1 required missing (3*0 = 0), 1 preferred missing (1*0 = 0)
        # Total weight = 3 + 3 + 3 + 1 = 10 -> Score = (6/10)*100 = 60
        assert score == 60

    def test_calculate_keyword_coverage(self, sample_models):
        jd, cv, _ = sample_models
        score = ScoringService.calculate_keyword_coverage(jd, cv)
        assert 0 <= score <= 100
        assert score > 50  # Contains C++, Qt, Linux, CAN

    def test_calculate_alignment_structure(self, sample_models):
        jd, cv, matches = sample_models
        service = ScoringService()
        result = service.calculate_alignment(jd, cv, matches)

        assert isinstance(result, AlignmentScore)
        assert 0 <= result.overall <= 100
        assert 0 <= result.technical_skills <= 100
        assert 0 <= result.experience_relevance <= 100
        assert "Phương pháp tính điểm" in result.methodology_notes


# === Priority Analyzer Tests ===

class TestPriorityAnalyzer:
    def test_get_top_recommendations(self, sample_models):
        _, _, matches = sample_models
        top = PriorityAnalyzer.get_top_recommendations(matches, limit=5)

        # Excludes ALREADY_STRONG matches
        assert len(top) == 2
        # First must be MUST_FIX (Docker)
        assert top[0].priority == Priority.MUST_FIX
        assert top[0].requirement == "Docker"
        # Second must be SHOULD_FIX (AUTOSAR)
        assert top[1].priority == Priority.SHOULD_FIX
        assert top[1].requirement == "AUTOSAR"


# === Report Generator Tests ===

class TestReportGenerator:
    def test_generate_markdown_contains_key_sections(self, sample_models):
        jd, cv, matches = sample_models
        scoring = ScoringService().calculate_alignment(jd, cv, matches)
        top = PriorityAnalyzer.get_top_recommendations(matches, limit=5)

        result = AnalysisResult(
            structured_jd=jd,
            structured_cv=cv,
            matches=matches,
            alignment_score=scoring,
            top_recommendations=top,
            suggestions=[
                CVSuggestion(
                    section="Projects",
                    original_text="Built with C++ and Qt",
                    suggested_text="Built with Modern C++ and Qt Widgets",
                    change_description="Emphasized Qt Widgets",
                    reason="Required by JD",
                    jd_requirement="Qt",
                    evidence="VTuber project in CV",
                    priority=Priority.MUST_FIX,
                )
            ],
            strong_count=2,
            partial_count=0,
            weak_count=0,
            missing_count=2,
            analyzed_at=datetime.now(),
            processing_time_seconds=1.5,
        )

        md = ReportGenerator.generate_markdown(result)
        assert "BÁO CÁO PHÂN TÍCH & TỐI ƯU HÓA CV" in md
        assert "ĐIỂM SỐ CV ↔ JD ALIGNMENT" in md
        assert "TOP CẦN CẢI THIỆN ĐẦU TIÊN" in md
        assert "GỢI Ý VIẾT LẠI CHI TIẾT" in md
        assert "Evidence First" in md
