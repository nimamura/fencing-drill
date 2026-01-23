"""Tests for session limit and timeout functionality."""
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest


class TestSessionTimestamps:
    """Test Session timestamp fields."""

    def test_session_has_created_at(self):
        """Session should have created_at timestamp."""
        from logic.session import BasicConfig, Session, TrainingMode

        session = Session(mode=TrainingMode.BASIC, config=BasicConfig())

        assert hasattr(session, "created_at")
        assert isinstance(session.created_at, datetime)

    def test_session_has_last_activity(self):
        """Session should have last_activity timestamp."""
        from logic.session import BasicConfig, Session, TrainingMode

        session = Session(mode=TrainingMode.BASIC, config=BasicConfig())

        assert hasattr(session, "last_activity")
        assert isinstance(session.last_activity, datetime)

    def test_session_timestamps_initialized_to_now(self):
        """Session timestamps should be initialized to creation time."""
        from logic.session import BasicConfig, Session, TrainingMode

        before = datetime.now()
        session = Session(mode=TrainingMode.BASIC, config=BasicConfig())
        after = datetime.now()

        assert before <= session.created_at <= after
        assert before <= session.last_activity <= after

    def test_touch_updates_last_activity(self):
        """touch() should update last_activity timestamp."""
        from logic.session import BasicConfig, Session, TrainingMode

        session = Session(mode=TrainingMode.BASIC, config=BasicConfig())
        original_activity = session.last_activity

        # Wait a tiny bit to ensure time difference
        with patch("logic.session.datetime") as mock_datetime:
            future_time = original_activity + timedelta(seconds=10)
            mock_datetime.now.return_value = future_time

            session.touch()

            assert session.last_activity == future_time
            assert session.last_activity > original_activity


class TestSessionLimitExceeded:
    """Test SessionLimitExceeded exception."""

    def test_session_limit_exceeded_exists(self):
        """SessionLimitExceeded exception should exist."""
        from logic.session import SessionLimitExceeded

        assert issubclass(SessionLimitExceeded, Exception)

    def test_session_limit_exceeded_message(self):
        """SessionLimitExceeded should accept a message."""
        from logic.session import SessionLimitExceeded

        exc = SessionLimitExceeded("Too many sessions")
        assert str(exc) == "Too many sessions"


class TestSessionManagerLimits:
    """Test SessionManager limit functionality."""

    def test_max_sessions_constant(self):
        """SessionManager should have MAX_SESSIONS constant."""
        from logic.session import SessionManager

        assert hasattr(SessionManager, "MAX_SESSIONS")
        assert SessionManager.MAX_SESSIONS == 100

    def test_session_timeout_constant(self):
        """SessionManager should have SESSION_TIMEOUT_MINUTES constant."""
        from logic.session import SessionManager

        assert hasattr(SessionManager, "SESSION_TIMEOUT_MINUTES")
        assert SessionManager.SESSION_TIMEOUT_MINUTES == 30

    def test_max_sessions_limit_raises_exception(self):
        """create_session should raise SessionLimitExceeded when limit reached."""
        from logic.session import (
            BasicConfig,
            SessionLimitExceeded,
            SessionManager,
            TrainingMode,
        )

        manager = SessionManager()
        # Fill up to limit
        for _ in range(SessionManager.MAX_SESSIONS):
            manager.create_session(mode=TrainingMode.BASIC, config=BasicConfig())

        # Next one should raise
        with pytest.raises(SessionLimitExceeded):
            manager.create_session(mode=TrainingMode.BASIC, config=BasicConfig())

    def test_cleanup_expired_sessions(self):
        """cleanup_expired should remove sessions older than timeout."""
        from logic.session import BasicConfig, SessionManager, TrainingMode

        manager = SessionManager()
        session = manager.create_session(mode=TrainingMode.BASIC, config=BasicConfig())

        # Simulate session being old
        old_time = datetime.now() - timedelta(minutes=31)
        session.last_activity = old_time

        manager.cleanup_expired()

        assert session.id not in manager.sessions

    def test_cleanup_keeps_active_sessions(self):
        """cleanup_expired should keep sessions within timeout."""
        from logic.session import BasicConfig, SessionManager, TrainingMode

        manager = SessionManager()
        session = manager.create_session(mode=TrainingMode.BASIC, config=BasicConfig())

        # Session is fresh, should not be cleaned up
        manager.cleanup_expired()

        assert session.id in manager.sessions

    def test_cleanup_before_create(self):
        """create_session should cleanup expired before checking limit."""
        from logic.session import BasicConfig, SessionManager, TrainingMode

        manager = SessionManager()

        # Fill up to limit
        for _ in range(SessionManager.MAX_SESSIONS):
            manager.create_session(mode=TrainingMode.BASIC, config=BasicConfig())

        # Make all sessions expired
        old_time = datetime.now() - timedelta(minutes=31)
        for session in manager.sessions.values():
            session.last_activity = old_time

        # Should succeed because cleanup runs first
        new_session = manager.create_session(
            mode=TrainingMode.BASIC, config=BasicConfig()
        )
        assert new_session is not None
        assert len(manager.sessions) == 1
