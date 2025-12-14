"""Tests for error handling - input validation, SSE errors, and edge cases."""
import pytest
from httpx import AsyncClient, ASGITransport


class TestInputValidation:
    """Test input validation for session start endpoint."""

    @pytest.mark.asyncio
    async def test_invalid_mode_returns_422(self):
        """POST /session/start with invalid mode should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "invalid_mode",
                    "repetitions": "10",
                    "tempo_bpm": "60",
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_repetitions_returns_422(self):
        """POST /session/start with negative repetitions should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "-5",
                    "tempo_bpm": "60",
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_zero_repetitions_returns_422(self):
        """POST /session/start with zero repetitions should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "0",
                    "tempo_bpm": "60",
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_tempo_too_low_returns_422(self):
        """POST /session/start with tempo below 30 BPM should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "10",
                    "tempo_bpm": "10",  # Below minimum of 30
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_tempo_too_high_returns_422(self):
        """POST /session/start with tempo above 120 BPM should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "10",
                    "tempo_bpm": "200",  # Above maximum of 120
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_command_id_returns_422(self):
        """POST /session/start with invalid command_id should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "nonexistent_command",
                    "repetitions": "10",
                    "tempo_bpm": "60",
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_command_set_returns_422(self):
        """POST /session/start with invalid command_set should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "random",
                    "command_set": "nonexistent_set",
                    "duration_seconds": "60",
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_pattern_id_returns_422(self):
        """POST /session/start with invalid pattern_id should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "combination",
                    "pattern_id": "Z",  # Invalid pattern
                    "repetitions": "10",
                    "tempo_bpm": "60",
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_duration_returns_422(self):
        """POST /session/start with negative duration should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "random",
                    "command_set": "beginner",
                    "duration_seconds": "-30",
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_min_interval_greater_than_max_returns_422(self):
        """POST /session/start with min_interval > max_interval should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "random",
                    "command_set": "beginner",
                    "duration_seconds": "60",
                    "min_interval_ms": "3000",
                    "max_interval_ms": "1000",  # min > max
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_sets_returns_422(self):
        """POST /session/start with negative sets should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "interval",
                    "work_seconds": "30",
                    "rest_seconds": "15",
                    "sets": "-1",
                    "tempo_bpm": "60",
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_repetitions_exceeds_max_returns_422(self):
        """POST /session/start with repetitions above 50 should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "100",  # Above max of 50
                    "tempo_bpm": "60",
                },
            )

        assert response.status_code == 422


class TestSSEErrors:
    """Test SSE endpoint error handling."""

    @pytest.mark.asyncio
    async def test_stream_without_session_id_returns_422(self):
        """GET /session/stream without session_id should return 422."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/session/stream")

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_stream_with_nonexistent_session_returns_404(self):
        """GET /session/stream with invalid session_id should return 404."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/session/stream?session_id=nonexistent-uuid"
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_stream_with_finished_session_returns_410(self):
        """GET /session/stream with finished session should return 410 Gone."""
        from main import app, session_manager
        from logic.session import TrainingMode, BasicConfig

        # Create and immediately finish a session
        session = session_manager.create_session(
            mode=TrainingMode.BASIC,
            config=BasicConfig(command_id="marche", repetitions=2, tempo_bpm=120),
        )
        session.stop()  # Mark as finished

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/session/stream?session_id={session.id}"
            )

        assert response.status_code == 410

        # Cleanup
        session_manager.remove_session(session.id)


class TestErrorResponseFormat:
    """Test that error responses include user-friendly messages."""

    @pytest.mark.asyncio
    async def test_validation_error_includes_detail(self):
        """Validation errors should include helpful detail messages."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "-5",
                    "tempo_bpm": "60",
                },
            )

        assert response.status_code == 422
        # Should return JSON with detail field
        json_response = response.json()
        assert "detail" in json_response

    @pytest.mark.asyncio
    async def test_404_error_includes_message(self):
        """404 errors should include descriptive message."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/settings/nonexistent")

        assert response.status_code == 404
        json_response = response.json()
        assert "detail" in json_response
        assert "nonexistent" in json_response["detail"].lower() or "invalid" in json_response["detail"].lower()
