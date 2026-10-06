"""Tests for Cover Letter generator service and endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock

from app.api.schemas.response import (
    ContactInfoResponse,
    ProjectResponse,
    SkillRequirementResponse,
    StructuredCVResponse,
    StructuredJDResponse,
)
from app.domain.enums import Importance, SkillCategory
from app.main import app
from app.services.cover_letter import CoverLetterService, _CoverLetterLLMOutput


@pytest.fixture
def sample_structured_jd():
    return StructuredJDResponse(
        job_title="Senior C++ Software Engineer",
        company="TechAuto GmbH",
        required_skills=[
            SkillRequirementResponse(
                name="C++",
                category=SkillCategory.TECHNICAL,
                importance=Importance.REQUIRED,
                keywords=["C++", "modern c++"],
            ),
            SkillRequirementResponse(
                name="Qt Framework",
                category=SkillCategory.TECHNICAL,
                importance=Importance.REQUIRED,
                keywords=["Qt Widgets", "QML"],
            ),
        ],
        responsibilities=["Develop Qt GUI applications", "Maintain C++ code"],
    )


@pytest.fixture
def sample_structured_cv():
    return StructuredCVResponse(
        name="Vo Van Tuan",
        contact=ContactInfoResponse(
            email="tuan@example.com",
            phone="0123456789",
            location="Ho Chi Minh City",
        ),
        technical_skills=["C++", "Qt", "Linux", "CAN bus"],
        projects=[
            ProjectResponse(
                name="VTuber Controller",
                description="Built a Qt Widgets UI application with signals and slots",
                technologies=["C++", "Qt Widgets"],
            )
        ],
    )


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_cover_letter_service_fallback(sample_structured_jd, sample_structured_cv):
    """CoverLetterService should generate fallback letter when LLM fails."""
    failing_llm = AsyncMock()
    failing_llm.generate_structured.side_effect = RuntimeError("API connection failure")

    service = CoverLetterService(llm_provider=failing_llm)
    res_vi = await service.generate_cover_letter(
        jd=sample_structured_jd,
        cv=sample_structured_cv,
        tone="professional",
        language="vi",
    )

    assert "Senior C++ Software Engineer" in res_vi.subject
    assert "TechAuto GmbH" in res_vi.salutation
    assert "Vo Van Tuan" in res_vi.sign_off
    assert res_vi.word_count > 50
    assert len(res_vi.body_paragraphs) >= 2

    # Test English fallback
    res_en = await service.generate_cover_letter(
        jd=sample_structured_jd,
        cv=sample_structured_cv,
        tone="enthusiastic",
        language="en",
    )
    assert "Dear Hiring Team" in res_en.salutation
    assert "TechAuto GmbH" in res_en.salutation
    assert "Sincerely" in res_en.sign_off


@pytest.mark.asyncio
async def test_cover_letter_service_with_mocked_llm(sample_structured_jd, sample_structured_cv):
    """CoverLetterService should assemble full letter when LLM succeeds."""
    mock_llm = AsyncMock()
    mock_llm.generate_structured.return_value = _CoverLetterLLMOutput(
        subject="Ứng tuyển Senior C++ Software Engineer — Vo Van Tuan",
        salutation="Kính gửi Ban Tuyển dụng TechAuto GmbH,",
        opening="Tôi rất vinh dự khi được ứng tuyển vào vị trí này.",
        body_paragraphs=[
            "Tôi đã có kinh nghiệm làm việc với C++ và Qt trong dự án VTuber Controller.",
            "Kỹ năng lập trình hệ thống của tôi đáp ứng tốt các yêu cầu phát triển phần mềm.",
        ],
        closing="Tôi mong muốn có cơ hội được phỏng vấn trực tiếp.",
        sign_off="Trân trọng,\n**Vo Van Tuan**",
        key_strengths_highlighted=["C++", "Qt Widgets"],
    )

    service = CoverLetterService(llm_provider=mock_llm)
    res = await service.generate_cover_letter(
        jd=sample_structured_jd,
        cv=sample_structured_cv,
        tone="professional",
        language="vi",
    )

    assert "Vo Van Tuan" in res.full_letter
    assert "VTuber Controller" in res.full_letter
    assert "C++" in res.key_strengths_highlighted
    assert res.word_count > 30


@pytest.mark.asyncio
async def test_cover_letter_endpoint(client: AsyncClient, sample_structured_jd, sample_structured_cv):
    """POST /api/v1/cover-letter/generate should return valid 200 CoverLetterResponse."""
    payload = {
        "structured_jd": sample_structured_jd.model_dump(),
        "structured_cv": sample_structured_cv.model_dump(),
        "tone": "professional",
        "language": "vi",
        "custom_instructions": "Nhấn mạnh kinh nghiệm C++ và hệ thống nhúng",
    }

    response = await client.post("/api/v1/cover-letter/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "subject" in data
    assert "full_letter" in data
    assert "body_paragraphs" in data
    assert data["word_count"] > 20
