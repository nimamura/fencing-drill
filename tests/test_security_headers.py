"""Tests for security headers middleware."""
import pytest
from httpx import ASGITransport, AsyncClient


class TestSecurityHeaders:
    """Test security headers are present in responses."""

    @pytest.mark.asyncio
    async def test_x_content_type_options_header(self):
        """Response should include X-Content-Type-Options: nosniff."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")

        assert response.headers.get("X-Content-Type-Options") == "nosniff"

    @pytest.mark.asyncio
    async def test_x_frame_options_header(self):
        """Response should include X-Frame-Options: DENY."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")

        assert response.headers.get("X-Frame-Options") == "DENY"

    @pytest.mark.asyncio
    async def test_x_xss_protection_header(self):
        """Response should include X-XSS-Protection: 1; mode=block."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")

        assert response.headers.get("X-XSS-Protection") == "1; mode=block"

    @pytest.mark.asyncio
    async def test_referrer_policy_header(self):
        """Response should include Referrer-Policy: strict-origin-when-cross-origin."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")

        assert (
            response.headers.get("Referrer-Policy")
            == "strict-origin-when-cross-origin"
        )

    @pytest.mark.asyncio
    async def test_security_headers_on_api_endpoint(self):
        """Security headers should be present on API endpoints too."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")

        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert (
            response.headers.get("Referrer-Policy")
            == "strict-origin-when-cross-origin"
        )
