"""E2E tests for session limit error handling."""
import pytest
from fastapi.testclient import TestClient


class TestSessionLimitE2E:
    """E2E tests for session limit API responses."""

    def test_session_limit_returns_429(self):
        """API should return 429 when session limit is exceeded."""
        from main import app, session_manager
        from logic.session import BasicConfig, TrainingMode

        client = TestClient(app)

        # Save original sessions and restore after test
        original_sessions = session_manager.sessions.copy()
        session_manager.sessions.clear()

        try:
            # Fill up to limit
            for _ in range(session_manager.MAX_SESSIONS):
                session_manager.create_session(
                    mode=TrainingMode.BASIC, config=BasicConfig()
                )

            # Make all sessions fresh to prevent cleanup
            from datetime import datetime
            for session in session_manager.sessions.values():
                session.last_activity = datetime.now()

            # Next request should get 429
            response = client.post(
                "/session/start",
                data={"mode": "basic"},
            )

            assert response.status_code == 429
            assert "data-i18n" in response.text  # Should have i18n attribute
        finally:
            # Restore original state
            session_manager.sessions = original_sessions

    def test_session_limit_error_message_is_user_friendly(self):
        """429 response should have user-friendly error message."""
        from main import app, session_manager
        from logic.session import BasicConfig, TrainingMode

        client = TestClient(app)

        original_sessions = session_manager.sessions.copy()
        session_manager.sessions.clear()

        try:
            # Fill up to limit
            for _ in range(session_manager.MAX_SESSIONS):
                session_manager.create_session(
                    mode=TrainingMode.BASIC, config=BasicConfig()
                )

            # Keep sessions fresh
            from datetime import datetime
            for session in session_manager.sessions.values():
                session.last_activity = datetime.now()

            response = client.post(
                "/session/start",
                data={"mode": "basic"},
            )

            # Should contain Japanese error message
            assert "混み合っています" in response.text or "しばらくお待ちください" in response.text
        finally:
            session_manager.sessions = original_sessions
