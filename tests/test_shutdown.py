"""Tests for graceful shutdown functionality."""
import logging

import pytest


class TestShutdownEvent:
    """Test shutdown event handler."""

    @pytest.mark.asyncio
    async def test_shutdown_event_cleans_sessions(self):
        """Shutdown event should stop all active sessions."""
        from logic.session import BasicConfig, SessionManager, SessionStatus, TrainingMode

        from main import app, session_manager

        # Create and start a session
        session = session_manager.create_session(
            mode=TrainingMode.BASIC, config=BasicConfig()
        )
        session.start()
        assert session.status == SessionStatus.RUNNING

        # Trigger shutdown event
        for handler in app.router.on_shutdown:
            await handler()

        # Session should be finished
        assert session.status == SessionStatus.FINISHED

    @pytest.mark.asyncio
    async def test_shutdown_event_logs_message(self, caplog):
        """Shutdown event should log a message."""
        from main import app

        with caplog.at_level(logging.INFO):
            # Trigger shutdown event
            for handler in app.router.on_shutdown:
                await handler()

        # Should log shutdown message
        log_messages = [record.message for record in caplog.records]
        assert any("shutdown" in msg.lower() for msg in log_messages)

    @pytest.mark.asyncio
    async def test_shutdown_clears_all_sessions(self):
        """Shutdown should clear all sessions from manager."""
        from logic.session import BasicConfig, TrainingMode

        from main import app, session_manager

        # Create multiple sessions
        for _ in range(3):
            session = session_manager.create_session(
                mode=TrainingMode.BASIC, config=BasicConfig()
            )
            session.start()

        assert len(session_manager.sessions) == 3

        # Trigger shutdown event
        for handler in app.router.on_shutdown:
            await handler()

        # All sessions should be cleared
        assert len(session_manager.sessions) == 0
