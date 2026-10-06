"""Tests for health check endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health_check_returns_ok(client: AsyncClient):
    """Health endpoint should return status ok."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_health_check_version_format(client: AsyncClient):
    """Health endpoint should return valid semver version."""
    response = await client.get("/api/v1/health")
    data = response.json()
    version = data["version"]
    parts = version.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
