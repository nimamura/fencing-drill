"""Tests for environment variable configuration."""
import pytest


class TestConfigDefaults:
    """Test default configuration values."""

    def test_session_limit_default(self):
        """Default SESSION_LIMIT should be 100."""
        from config import settings

        assert settings.session_limit == 100

    def test_session_timeout_default(self):
        """Default SESSION_TIMEOUT_MINUTES should be 30."""
        from config import settings

        assert settings.session_timeout_minutes == 30

    def test_log_level_default(self):
        """Default LOG_LEVEL should be INFO."""
        from config import settings

        assert settings.log_level == "INFO"

    def test_base_url_default(self):
        """Default BASE_URL should be empty string."""
        from config import settings

        assert settings.base_url == ""


class TestConfigFromEnv:
    """Test configuration from environment variables."""

    def test_session_limit_from_env(self, monkeypatch):
        """SESSION_LIMIT should be configurable via env var."""
        monkeypatch.setenv("SESSION_LIMIT", "50")

        # Re-import to pick up new env var
        import importlib
        import config

        importlib.reload(config)

        assert config.settings.session_limit == 50

    def test_session_timeout_from_env(self, monkeypatch):
        """SESSION_TIMEOUT_MINUTES should be configurable via env var."""
        monkeypatch.setenv("SESSION_TIMEOUT_MINUTES", "60")

        import importlib
        import config

        importlib.reload(config)

        assert config.settings.session_timeout_minutes == 60

    def test_log_level_from_env(self, monkeypatch):
        """LOG_LEVEL should be configurable via env var."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        import importlib
        import config

        importlib.reload(config)

        assert config.settings.log_level == "DEBUG"

    def test_base_url_from_env(self, monkeypatch):
        """BASE_URL should be configurable via env var."""
        monkeypatch.setenv("BASE_URL", "https://example.com")

        import importlib
        import config

        importlib.reload(config)

        assert config.settings.base_url == "https://example.com"


class TestSessionManagerUsesConfig:
    """Test that SessionManager uses config values."""

    def test_session_manager_uses_config_limit(self, monkeypatch):
        """SessionManager should use SESSION_LIMIT from config."""
        monkeypatch.setenv("SESSION_LIMIT", "5")

        import importlib
        import config
        from logic import session

        importlib.reload(config)
        importlib.reload(session)

        from logic.session import BasicConfig, SessionLimitExceeded, SessionManager, TrainingMode

        manager = SessionManager()

        # Fill up to limit
        for _ in range(5):
            manager.create_session(mode=TrainingMode.BASIC, config=BasicConfig())

        # Next one should raise
        with pytest.raises(SessionLimitExceeded):
            manager.create_session(mode=TrainingMode.BASIC, config=BasicConfig())

    def test_session_manager_uses_config_timeout(self, monkeypatch):
        """SessionManager should use SESSION_TIMEOUT_MINUTES from config."""
        from datetime import datetime, timedelta

        monkeypatch.setenv("SESSION_TIMEOUT_MINUTES", "5")

        import importlib
        import config
        from logic import session

        importlib.reload(config)
        importlib.reload(session)

        from logic.session import BasicConfig, SessionManager, TrainingMode

        manager = SessionManager()
        s = manager.create_session(mode=TrainingMode.BASIC, config=BasicConfig())

        # Set session to 6 minutes old (past 5-minute timeout)
        s.last_activity = datetime.now() - timedelta(minutes=6)

        manager.cleanup_expired()

        assert s.id not in manager.sessions
