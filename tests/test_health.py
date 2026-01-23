"""Tests for health check endpoint."""
import pytest
from httpx import ASGITransport, AsyncClient


class TestHealthEndpoint:
    """Test the health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_200(self):
        """GET /health should return 200 status code."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_json(self):
        """GET /health should return {"status": "ok"} JSON response."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")

        assert response.json() == {"status": "ok"}
