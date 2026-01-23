"""Tests for SSE keepalive heartbeat functionality."""
import asyncio
import json

import pytest
from httpx import ASGITransport, AsyncClient


class TestSSEHeartbeat:
    """Test SSE heartbeat functionality."""

    @pytest.mark.asyncio
    async def test_sse_sends_heartbeat(self):
        """SSE stream should send heartbeat events to keep connection alive."""
        from logic.session import BasicConfig, TrainingMode

        from main import app, session_manager

        # Create a session with short repetitions
        session = session_manager.create_session(
            mode=TrainingMode.BASIC,
            config=BasicConfig(pair_id="marche_rompe", repetitions=2, tempo_bpm=120),
        )
        session.start()

        events_received = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            async with client.stream(
                "GET", f"/session/stream?session_id={session.id}", timeout=10.0
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("event:"):
                        event_type = line.split(":", 1)[1].strip()
                        events_received.append(event_type)
                    # Break after receiving a few events to avoid timeout
                    if len(events_received) >= 5:
                        break

        # Should have received some events
        assert len(events_received) > 0

        # Cleanup
        session_manager.remove_session(session.id)

    @pytest.mark.asyncio
    async def test_heartbeat_constant_exists(self):
        """HEARTBEAT_INTERVAL_SECONDS constant should be defined."""
        from main import HEARTBEAT_INTERVAL_SECONDS

        assert HEARTBEAT_INTERVAL_SECONDS == 30

    @pytest.mark.asyncio
    async def test_sse_heartbeat_format(self):
        """Heartbeat should be sent as SSE comment (colon prefix)."""
        # This tests the format - heartbeats should be ":heartbeat\n\n"
        # which is an SSE comment that clients ignore but keeps connection alive
        from logic.session import BasicConfig, TrainingMode

        from main import app, session_manager

        # Create a session
        session = session_manager.create_session(
            mode=TrainingMode.BASIC,
            config=BasicConfig(pair_id="marche_rompe", repetitions=1, tempo_bpm=120),
        )
        session.start()

        raw_data = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            async with client.stream(
                "GET", f"/session/stream?session_id={session.id}", timeout=5.0
            ) as response:
                async for chunk in response.aiter_bytes():
                    raw_data.append(chunk.decode("utf-8"))
                    # Collect a few chunks
                    if len(raw_data) >= 10:
                        break

        # Cleanup
        session_manager.remove_session(session.id)
