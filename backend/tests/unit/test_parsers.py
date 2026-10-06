"""Unit tests for JDParserService and CVParserService with mocked LLM provider."""

import pytest
from typing import TypeVar
from pydantic import BaseModel

from app.domain.enums import Importance, SkillCategory
from app.domain.models import StructuredJD, StructuredCV
from app.providers.llm.base import LLMProvider
from app.services.jd_parser import JDParserService, _JDExtractionResponse, _SkillExtraction
from app.services.cv_parser import (
    CVParserService,
    _CVExtractionResponse,
    _EducationExtraction,
    _ProjectExtraction,
    _ContactExtraction,
)

T = TypeVar("T", bound=BaseModel)


class DummyModel(BaseModel):
    pass


class MockLLMProvider(LLMProvider):
    """Mock LLM Provider for unit testing."""

    def __init__(self, mock_response: BaseModel) -> None:
        self.mock_response = mock_response

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> str:
        return "mock text"

    async def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
        system_prompt: str | None = None,
        temperature: float = 0.1,
    ) -> T:
        return self.mock_response  # type: ignore[return-value]


# === JD Parser Tests ===

class TestJDParserService:
    @pytest.mark.asyncio
    async def test_parse_jd_success(self):
        mock_jd = _JDExtractionResponse(
            job_title="Senior C++ Software Engineer",
            company="TechAuto",
            location="Ho Chi Minh City",
            employment_type="Full-time",
            seniority_level="Senior",
            required_skills=[
                _SkillExtraction(
                    name="C++",
                    category=SkillCategory.TECHNICAL,
                    importance=Importance.REQUIRED,
                    context="3+ years experience",
                    keywords=["C++", "Modern C++"],
                ),
                _SkillExtraction(
                    name="Qt",
                    category=SkillCategory.TECHNICAL,
                    importance=Importance.REQUIRED,
                    context="Qt Widgets, QML",
                    keywords=["Qt", "QML"],
                ),
            ],
            preferred_skills=[
                _SkillExtraction(
                    name="Docker",
                    category=SkillCategory.TOOL,
                    importance=Importance.PREFERRED,
                    context="CI/CD experience",
                    keywords=["Docker"],
                )
            ],
            responsibilities=["Develop C++ automotive applications"],
            education_requirements=["Bachelor degree in Computer Science"],
            technical_requirements=["CAN", "Linux"],
            keywords=["C++", "Qt", "CAN", "Linux"],
        )

        service = JDParserService(llm_provider=MockLLMProvider(mock_jd))
        result = await service.parse("Sample JD content")

        assert isinstance(result, StructuredJD)
        assert result.job_title == "Senior C++ Software Engineer"
        assert len(result.required_skills) == 2
        assert result.required_skills[0].name == "C++"
        assert result.required_skills[0].importance == Importance.REQUIRED
        assert len(result.preferred_skills) == 1
        assert result.preferred_skills[0].name == "Docker"
        assert "CAN" in result.technical_requirements

    @pytest.mark.asyncio
    async def test_parse_empty_jd_raises_error(self):
        service = JDParserService(llm_provider=MockLLMProvider(DummyModel()))
        with pytest.raises(ValueError, match="không được để trống"):
            await service.parse("   ")


# === CV Parser Tests ===

class TestCVParserService:
    @pytest.mark.asyncio
    async def test_parse_cv_success(self):
        mock_cv = _CVExtractionResponse(
            name="Võ Văn Tuấn",
            title="Fresher C++ Developer",
            summary="Passionate developer in embedded systems",
            contact=_ContactExtraction(
                email="tuan@example.com",
                phone="+84 123 456 789",
                location="Ho Chi Minh City",
            ),
            education=[
                _EducationExtraction(
                    institution="HCMUT",
                    degree="Bachelor",
                    field="Computer Engineering",
                    gpa="3.2/4.0",
                )
            ],
            projects=[
                _ProjectExtraction(
                    name="VTuber Avatar Control Panel",
                    description="Developed Qt Widgets app",
                    technologies=["C++", "Qt", "Qt Creator"],
                    highlights=["Signal/slot communication"],
                )
            ],
            technical_skills=["C++", "Qt", "Linux", "FreeRTOS", "CAN"],
            languages=["Vietnamese", "English"],
        )

        service = CVParserService(llm_provider=MockLLMProvider(mock_cv))
        result = await service.parse("Sample CV content")

        assert isinstance(result, StructuredCV)
        assert result.name == "Võ Văn Tuấn"
        assert result.contact.email == "tuan@example.com"
        assert len(result.education) == 1
        assert result.education[0].institution == "HCMUT"
        assert len(result.projects) == 1
        assert result.projects[0].name == "VTuber Avatar Control Panel"
        assert "Qt" in result.projects[0].technologies
        assert "C++" in result.technical_skills

    @pytest.mark.asyncio
    async def test_parse_empty_cv_raises_error(self):
        service = CVParserService(llm_provider=MockLLMProvider(DummyModel()))
        with pytest.raises(ValueError, match="không được để trống"):
            await service.parse("")
