"""Tests for logic/session.py - Session state management."""
import pytest
from enum import Enum


class TestSessionStatus:
    """Test SessionStatus enum."""

    def test_session_status_values(self):
        """SessionStatus should have idle, running, paused, finished states."""
        from logic.session import SessionStatus

        assert SessionStatus.IDLE.value == "idle"
        assert SessionStatus.RUNNING.value == "running"
        assert SessionStatus.PAUSED.value == "paused"
        assert SessionStatus.FINISHED.value == "finished"


class TestTrainingMode:
    """Test TrainingMode enum."""

    def test_training_mode_values(self):
        """TrainingMode should have basic, combination, random, interval modes."""
        from logic.session import TrainingMode

        assert TrainingMode.BASIC.value == "basic"
        assert TrainingMode.COMBINATION.value == "combination"
        assert TrainingMode.RANDOM.value == "random"
        assert TrainingMode.INTERVAL.value == "interval"


class TestSessionConfig:
    """Test session configuration dataclasses."""

    def test_basic_config_defaults(self):
        """BasicConfig should have sensible defaults."""
        from logic.session import BasicConfig

        config = BasicConfig()
        assert config.command_id == "marche"
        assert config.repetitions == 10
        assert config.tempo_bpm == 60

    def test_basic_config_custom_values(self):
        """BasicConfig should accept custom values."""
        from logic.session import BasicConfig

        config = BasicConfig(command_id="rompe", repetitions=20, tempo_bpm=90)
        assert config.command_id == "rompe"
        assert config.repetitions == 20
        assert config.tempo_bpm == 90

    def test_random_config_defaults(self):
        """RandomConfig should have sensible defaults."""
        from logic.session import RandomConfig

        config = RandomConfig()
        assert config.command_set == "beginner"
        assert config.duration_seconds == 60
        assert config.min_interval_ms == 1000
        assert config.max_interval_ms == 3000

    def test_interval_config_defaults(self):
        """IntervalConfig should have sensible defaults."""
        from logic.session import IntervalConfig

        config = IntervalConfig()
        assert config.work_seconds == 30
        assert config.rest_seconds == 15
        assert config.sets == 5
        assert config.tempo_bpm == 90


class TestSession:
    """Test Session class."""

    def test_create_session_with_id(self):
        """Session should be created with a unique ID."""
        from logic.session import Session, TrainingMode, BasicConfig

        session = Session(mode=TrainingMode.BASIC, config=BasicConfig())

        assert session.id is not None
        assert len(session.id) > 0

    def test_session_initial_status(self):
        """Session should start in IDLE status."""
        from logic.session import Session, TrainingMode, BasicConfig, SessionStatus

        session = Session(mode=TrainingMode.BASIC, config=BasicConfig())

        assert session.status == SessionStatus.IDLE

    def test_session_start(self):
        """Session should transition to RUNNING on start."""
        from logic.session import Session, TrainingMode, BasicConfig, SessionStatus

        session = Session(mode=TrainingMode.BASIC, config=BasicConfig())
        session.start()

        assert session.status == SessionStatus.RUNNING

    def test_session_stop(self):
        """Session should transition to FINISHED on stop."""
        from logic.session import Session, TrainingMode, BasicConfig, SessionStatus

        session = Session(mode=TrainingMode.BASIC, config=BasicConfig())
        session.start()
        session.stop()

        assert session.status == SessionStatus.FINISHED

    def test_session_stores_mode(self):
        """Session should store training mode."""
        from logic.session import Session, TrainingMode, BasicConfig

        session = Session(mode=TrainingMode.BASIC, config=BasicConfig())

        assert session.mode == TrainingMode.BASIC

    def test_session_stores_config(self):
        """Session should store configuration."""
        from logic.session import Session, TrainingMode, BasicConfig

        config = BasicConfig(command_id="rompe", repetitions=15)
        session = Session(mode=TrainingMode.BASIC, config=config)

        assert session.config.command_id == "rompe"
        assert session.config.repetitions == 15


class TestSessionManager:
    """Test SessionManager for managing multiple sessions."""

    def test_create_session(self):
        """SessionManager should create and store a session."""
        from logic.session import SessionManager, TrainingMode, BasicConfig

        manager = SessionManager()
        session = manager.create_session(
            mode=TrainingMode.BASIC, config=BasicConfig()
        )

        assert session is not None
        assert session.id in manager.sessions

    def test_get_session(self):
        """SessionManager should retrieve session by ID."""
        from logic.session import SessionManager, TrainingMode, BasicConfig

        manager = SessionManager()
        session = manager.create_session(
            mode=TrainingMode.BASIC, config=BasicConfig()
        )

        retrieved = manager.get_session(session.id)
        assert retrieved is session

    def test_get_nonexistent_session(self):
        """SessionManager should return None for nonexistent session."""
        from logic.session import SessionManager

        manager = SessionManager()
        result = manager.get_session("nonexistent-id")

        assert result is None

    def test_remove_session(self):
        """SessionManager should remove session by ID."""
        from logic.session import SessionManager, TrainingMode, BasicConfig

        manager = SessionManager()
        session = manager.create_session(
            mode=TrainingMode.BASIC, config=BasicConfig()
        )

        manager.remove_session(session.id)

        assert session.id not in manager.sessions

    def test_get_active_session(self):
        """SessionManager should track active (running) session."""
        from logic.session import SessionManager, TrainingMode, BasicConfig

        manager = SessionManager()
        session = manager.create_session(
            mode=TrainingMode.BASIC, config=BasicConfig()
        )
        session.start()

        active = manager.get_active_session()
        assert active is session

    def test_no_active_session_when_idle(self):
        """SessionManager should return None when no session is running."""
        from logic.session import SessionManager, TrainingMode, BasicConfig

        manager = SessionManager()
        manager.create_session(mode=TrainingMode.BASIC, config=BasicConfig())

        active = manager.get_active_session()
        assert active is None
