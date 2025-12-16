"""Tests for main.py - FastAPI application and API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport


class TestAppSetup:
    """Test FastAPI application setup."""

    def test_app_exists(self):
        """FastAPI app should be importable."""
        from main import app
        assert app is not None

    def test_app_has_title(self):
        """App should have a title."""
        from main import app
        assert app.title == "Fencing Drill"


class TestRootEndpoint:
    """Test the root endpoint."""

    @pytest.mark.asyncio
    async def test_root_returns_html(self):
        """GET / should return HTML."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestSessionStartEndpoint:
    """Test the session start endpoint."""

    @pytest.mark.asyncio
    async def test_start_session_basic_mode(self):
        """POST /session/start should create a basic mode session."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "10",
                    "tempo_bpm": "60",
                },
            )

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_start_session_returns_session_id(self):
        """POST /session/start should return session ID in response."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "10",
                    "tempo_bpm": "60",
                },
            )

        # Response should contain data-session-id attribute
        assert "data-session-id" in response.text


class TestSessionStopEndpoint:
    """Test the session stop endpoint."""

    @pytest.mark.asyncio
    async def test_stop_session(self):
        """POST /session/stop should stop the session."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # First start a session
            start_response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "10",
                    "tempo_bpm": "60",
                },
            )

            # Then stop it
            response = await client.post("/session/stop")

        assert response.status_code == 200


class TestSettingsEndpoint:
    """Test the settings endpoint."""

    @pytest.mark.asyncio
    async def test_get_basic_settings(self):
        """GET /settings/basic should return HTML fragment."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/settings/basic")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_get_random_settings(self):
        """GET /settings/random should return HTML fragment."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/settings/random")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_get_invalid_mode_settings(self):
        """GET /settings/invalid should return 404."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/settings/invalid")

        assert response.status_code == 404


class TestSSEEndpoint:
    """Test the SSE stream endpoint."""

    @pytest.mark.asyncio
    async def test_stream_endpoint_exists(self):
        """GET /session/stream should return event stream."""
        from main import app, session_manager
        from logic.session import TrainingMode, BasicConfig

        # Create session directly via session manager
        session = session_manager.create_session(
            mode=TrainingMode.BASIC,
            config=BasicConfig(command_id="marche", repetitions=2, tempo_bpm=120)
        )
        session.start()

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Connect to stream with session_id
            response = await client.get(f"/session/stream?session_id={session.id}", timeout=1.0)

        # Should return event-stream content type
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        # Cleanup
        session_manager.remove_session(session.id)


class TestWeaponParameter:
    """Test weapon parameter in session start."""

    @pytest.mark.asyncio
    async def test_start_session_with_weapon_foil(self):
        """POST /session/start with weapon=foil should succeed."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "10",
                    "tempo_bpm": "60",
                    "weapon": "foil",
                },
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_start_session_with_weapon_epee(self):
        """POST /session/start with weapon=epee should succeed."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "10",
                    "tempo_bpm": "60",
                    "weapon": "epee",
                },
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_start_session_with_weapon_sabre(self):
        """POST /session/start with weapon=sabre should succeed."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "10",
                    "tempo_bpm": "60",
                    "weapon": "sabre",
                },
            )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_start_session_with_invalid_weapon(self):
        """POST /session/start with invalid weapon should return 422."""
        from main import app

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "10",
                    "tempo_bpm": "60",
                    "weapon": "katana",
                },
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_start_session_default_weapon_is_foil(self):
        """POST /session/start without weapon should default to foil."""
        from main import app, session_manager

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/session/start",
                data={
                    "mode": "basic",
                    "command_id": "marche",
                    "repetitions": "10",
                    "tempo_bpm": "60",
                },
            )

        assert response.status_code == 200
        # Session should have been created with default weapon=foil
        active_session = session_manager.get_active_session()
        if active_session:
            assert active_session.config.weapon == "foil"
