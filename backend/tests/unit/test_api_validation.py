"""Tests for request validation."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_analyze_missing_jd_returns_400(client: AsyncClient):
    """Should return 400 when no JD is provided."""
    response = await client.post(
        "/api/v1/analyze",
        data={"cv_text": "Some CV text"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "MISSING_JD"


@pytest.mark.asyncio
async def test_analyze_missing_cv_returns_400(client: AsyncClient):
    """Should return 400 when no CV is provided."""
    response = await client.post(
        "/api/v1/analyze",
        data={"jd_text": "Some JD text"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "MISSING_CV"


@pytest.mark.asyncio
async def test_analyze_missing_both_returns_400(client: AsyncClient):
    """Should return 400 when neither JD nor CV is provided."""
    response = await client.post("/api/v1/analyze")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_analyze_invalid_file_format_returns_400(client: AsyncClient):
    """Should return 400 for unsupported file format."""
    response = await client.post(
        "/api/v1/analyze",
        files={
            "jd_file": ("job.xlsx", b"fake content", "application/octet-stream"),
            "cv_file": ("cv.txt", b"Some CV", "text/plain"),
        },
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_FILE_FORMAT"


@pytest.mark.asyncio
async def test_analyze_valid_input_reaches_pipeline(client: AsyncClient, monkeypatch):
    """Valid input should execute pipeline and return 200 when pipeline succeeds."""
    from datetime import datetime
    from unittest.mock import AsyncMock
    from app.services.pipeline import AnalysisPipeline
    from app.domain.models import (
        AnalysisResult,
        StructuredJD,
        StructuredCV,
        AlignmentScore,
    )

    mock_result = AnalysisResult(
        structured_jd=StructuredJD(job_title="C++ Dev", raw_text="C++"),
        structured_cv=StructuredCV(name="Tuan", raw_text="Tuan"),
        matches=[],
        alignment_score=AlignmentScore(
            overall=80,
            technical_skills=80,
            experience_relevance=80,
            responsibilities_alignment=80,
            keyword_coverage=80,
            education_alignment=80,
            cv_clarity=80,
            methodology_notes="Notes",
        ),
        top_recommendations=[],
        suggestions=[],
        strong_count=0,
        partial_count=0,
        weak_count=0,
        missing_count=0,
        analyzed_at=datetime.now(),
        processing_time_seconds=1.0,
    )

    monkeypatch.setattr(AnalysisPipeline, "run", AsyncMock(return_value=mock_result))

    response = await client.post(
        "/api/v1/analyze",
        data={
            "jd_text": "Senior C++ Developer needed",
            "cv_text": "Experienced C++ developer with 5 years",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["structured_jd"]["job_title"] == "C++ Dev"
    assert data["structured_cv"]["name"] == "Tuan"
    assert data["alignment_score"]["overall"] == 80
