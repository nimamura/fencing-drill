"""Tests for session recovery on disconnect."""
import pytest
from httpx import AsyncClient, ASGITransport


class TestSessionProgress:
    """Test session progress tracking."""

    def test_session_tracks_current_rep(self):
        """Session should track current repetition."""
        from logic.session import (
            BasicConfig,
            Session,
            SessionStatus,
            TrainingMode,
        )

        session = Session(
            mode=TrainingMode.BASIC,
            config=BasicConfig(command_id="marche", repetitions=10, tempo_bpm=60),
        )
        session.start()

        # Progress should be trackable
        session.progress = {"current_rep": 5, "total_reps": 10}
        assert session.progress["current_rep"] == 5
        assert session.progress["total_reps"] == 10

    def test_session_tracks_elapsed_time(self):
        """Session should track elapsed time for random/interval modes."""
        from logic.session import (
            RandomConfig,
            Session,
            SessionStatus,
            TrainingMode,
        )

        session = Session(
            mode=TrainingMode.RANDOM,
            config=RandomConfig(
                command_set="beginner", duration_seconds=60, min_interval_ms=1000
            ),
        )
        session.start()

        # Progress should track elapsed time
        session.progress = {"elapsed_seconds": 30, "total_seconds": 60}
        assert session.progress["elapsed_seconds"] == 30

    def test_session_tracks_interval_set(self):
        """Session should track current set for interval mode."""
        from logic.session import (
            IntervalConfig,
            Session,
            TrainingMode,
        )

        session = Session(
            mode=TrainingMode.INTERVAL,
            config=IntervalConfig(work_seconds=30, rest_seconds=15, sets=5),
        )
        session.start()

        session.progress = {
            "current_set": 3,
            "total_sets": 5,
            "phase": "work",
            "phase_elapsed": 15,
        }
        assert session.progress["current_set"] == 3
        assert session.progress["phase"] == "work"


class TestSessionPauseResume:
    """Test session pause and resume functionality."""

    def test_session_can_pause(self):
        """Session should be pauseable."""
        from logic.session import (
            BasicConfig,
            Session,
            SessionStatus,
            TrainingMode,
        )

        session = Session(
            mode=TrainingMode.BASIC,
            config=BasicConfig(command_id="marche", repetitions=10, tempo_bpm=60),
        )
        session.start()
        assert session.status == SessionStatus.RUNNING

        session.pause()
        assert session.status == SessionStatus.PAUSED

    def test_session_can_resume_after_pause(self):
        """Session should be resumable after pause."""
        from logic.session import (
            BasicConfig,
            Session,
            SessionStatus,
            TrainingMode,
        )

        session = Session(
            mode=TrainingMode.BASIC,
            config=BasicConfig(command_id="marche", repetitions=10, tempo_bpm=60),
        )
        session.start()
        session.progress = {"current_rep": 5}
        session.pause()

        session.resume()
        assert session.status == SessionStatus.RUNNING
        assert session.progress["current_rep"] == 5

    def test_paused_session_preserves_progress(self):
        """Paused session should preserve progress info."""
        from logic.session import (
            BasicConfig,
            Session,
            SessionStatus,
            TrainingMode,
        )

        session = Session(
            mode=TrainingMode.BASIC,
            config=BasicConfig(command_id="marche", repetitions=10, tempo_bpm=60),
        )
        session.start()
        session.progress = {"current_rep": 7, "total_reps": 10}
        session.pause()

        # Progress should still be available
        assert session.progress["current_rep"] == 7
        assert session.progress["total_reps"] == 10


class TestSessionRecoveryAPI:
    """Test session recovery via API endpoints."""

    @pytest.mark.asyncio
    async def test_get_session_status(self):
        """GET /session/status should return current session status."""
        from main import app, session_manager
        from logic.session import TrainingMode, BasicConfig

        # Create a running session
        session = session_manager.create_session(
            mode=TrainingMode.BASIC,
            config=BasicConfig(command_id="marche", repetitions=10, tempo_bpm=60),
        )
        session.start()
        session.progress = {"current_rep": 5, "total_reps": 10}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(f"/session/status?session_id={session.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["progress"]["current_rep"] == 5

        # Cleanup
        session_manager.remove_session(session.id)

    @pytest.mark.asyncio
    async def test_pause_session(self):
        """POST /session/pause should pause a running session."""
        from main import app, session_manager
        from logic.session import TrainingMode, BasicConfig, SessionStatus

        session = session_manager.create_session(
            mode=TrainingMode.BASIC,
            config=BasicConfig(command_id="marche", repetitions=10, tempo_bpm=60),
        )
        session.start()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(f"/session/pause?session_id={session.id}")

        assert response.status_code == 200
        assert session.status == SessionStatus.PAUSED

        # Cleanup
        session_manager.remove_session(session.id)

    @pytest.mark.asyncio
    async def test_resume_session(self):
        """POST /session/resume should resume a paused session."""
        from main import app, session_manager
        from logic.session import TrainingMode, BasicConfig, SessionStatus

        session = session_manager.create_session(
            mode=TrainingMode.BASIC,
            config=BasicConfig(command_id="marche", repetitions=10, tempo_bpm=60),
        )
        session.start()
        session.pause()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(f"/session/resume?session_id={session.id}")

        assert response.status_code == 200
        assert session.status == SessionStatus.RUNNING

        # Cleanup
        session_manager.remove_session(session.id)

    @pytest.mark.asyncio
    async def test_pause_nonexistent_session_returns_404(self):
        """POST /session/pause with invalid session should return 404."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/session/pause?session_id=nonexistent")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_resume_nonexistent_session_returns_404(self):
        """POST /session/resume with invalid session should return 404."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post("/session/resume?session_id=nonexistent")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_status_nonexistent_session_returns_404(self):
        """GET /session/status with invalid session should return 404."""
        from main import app

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/session/status?session_id=nonexistent")

        assert response.status_code == 404


class TestSSEReconnection:
    """Test SSE reconnection behavior."""

    @pytest.mark.asyncio
    async def test_stream_paused_session_returns_paused_status(self):
        """GET /session/stream for paused session should indicate paused."""
        from main import app, session_manager
        from logic.session import TrainingMode, BasicConfig

        session = session_manager.create_session(
            mode=TrainingMode.BASIC,
            config=BasicConfig(command_id="marche", repetitions=10, tempo_bpm=60),
        )
        session.start()
        session.pause()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/session/stream?session_id={session.id}", timeout=1.0
            )

        # Should return 409 Conflict for paused session
        assert response.status_code == 409

        # Cleanup
        session_manager.remove_session(session.id)
