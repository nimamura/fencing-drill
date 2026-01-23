"""Tests for logging functionality."""
import logging

import pytest
from httpx import ASGITransport, AsyncClient


class TestStartupLogging:
    """Test logging at application startup."""

    def test_startup_logs_message(self, caplog):
        """Application startup should log a message."""
        with caplog.at_level(logging.INFO):
            # Re-import to trigger startup logging setup
            import importlib
            import main

            importlib.reload(main)

        # Should log startup message
        assert any("Fencing Drill" in record.message for record in caplog.records)


class TestRequestLogging:
    """Test request logging middleware."""

    @pytest.mark.asyncio
    async def test_request_logging_middleware(self, caplog):
        """Requests should be logged with method and path."""
        from main import app

        with caplog.at_level(logging.INFO):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                await client.get("/health")

        # Should log the request
        log_messages = [record.message for record in caplog.records]
        assert any("GET" in msg and "/health" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_request_logging_includes_status_code(self, caplog):
        """Request log should include response status code."""
        from main import app

        with caplog.at_level(logging.INFO):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                await client.get("/health")

        # Should log the status code
        log_messages = [record.message for record in caplog.records]
        assert any("200" in msg for msg in log_messages)
