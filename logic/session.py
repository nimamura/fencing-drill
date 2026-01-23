"""Session state management for training sessions."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Union

from config import settings


class SessionLimitExceeded(Exception):
    """Raised when the maximum number of sessions is exceeded."""

    pass


class SessionStatus(Enum):
    """Status of a training session."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"


class TrainingMode(Enum):
    """Available training modes."""

    BASIC = "basic"
    COMBINATION = "combination"
    RANDOM = "random"
    INTERVAL = "interval"


@dataclass
class BasicConfig:
    """Configuration for Basic training mode."""

    pair_id: str = "marche_rompe"
    repetitions: int = 10
    tempo_bpm: int = 60
    weapon: str = "foil"


@dataclass
class CombinationConfig:
    """Configuration for Combination training mode."""

    pattern_id: str = "A"
    repetitions: int = 5
    tempo_bpm: int = 60
    weapon: str = "foil"


@dataclass
class RandomConfig:
    """Configuration for Random training mode."""

    command_set: str = "beginner"
    duration_seconds: int = 60
    min_interval_ms: int = 1000
    max_interval_ms: int = 3000
    weapon: str = "foil"


@dataclass
class IntervalConfig:
    """Configuration for Interval training mode."""

    work_seconds: int = 30
    rest_seconds: int = 15
    sets: int = 5
    tempo_bpm: int = 90
    weapon: str = "foil"


# Type alias for any config type
SessionConfig = Union[BasicConfig, CombinationConfig, RandomConfig, IntervalConfig]


@dataclass
class Session:
    """A training session."""

    mode: TrainingMode
    config: SessionConfig
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: SessionStatus = SessionStatus.IDLE
    progress: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    def start(self) -> None:
        """Start the session."""
        self.status = SessionStatus.RUNNING

    def stop(self) -> None:
        """Stop the session."""
        self.status = SessionStatus.FINISHED

    def pause(self) -> None:
        """Pause the session."""
        self.status = SessionStatus.PAUSED

    def resume(self) -> None:
        """Resume a paused session."""
        self.status = SessionStatus.RUNNING

    def touch(self) -> None:
        """Update last_activity timestamp."""
        self.last_activity = datetime.now()


class SessionManager:
    """Manages training sessions."""

    @property
    def MAX_SESSIONS(self) -> int:
        """Maximum number of concurrent sessions."""
        return settings.session_limit

    @property
    def SESSION_TIMEOUT_MINUTES(self) -> int:
        """Session timeout in minutes."""
        return settings.session_timeout_minutes

    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}

    def cleanup_expired(self) -> None:
        """Remove sessions that have exceeded the timeout."""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(minutes=self.SESSION_TIMEOUT_MINUTES)
        expired_ids = [
            sid for sid, session in self.sessions.items()
            if session.last_activity < cutoff
        ]
        for sid in expired_ids:
            del self.sessions[sid]

    def create_session(
        self, mode: TrainingMode, config: SessionConfig
    ) -> Session:
        """Create a new training session.

        Args:
            mode: The training mode.
            config: The configuration for the mode.

        Returns:
            The created Session.

        Raises:
            SessionLimitExceeded: If the maximum number of sessions is reached.
        """
        # Cleanup expired sessions first
        self.cleanup_expired()

        # Check limit
        if len(self.sessions) >= self.MAX_SESSIONS:
            raise SessionLimitExceeded(
                f"Maximum number of sessions ({self.MAX_SESSIONS}) reached"
            )

        session = Session(mode=mode, config=config)
        self.sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            The Session if found, None otherwise.
        """
        return self.sessions.get(session_id)

    def remove_session(self, session_id: str) -> None:
        """Remove a session by ID.

        Args:
            session_id: The session identifier.
        """
        self.sessions.pop(session_id, None)

    def get_active_session(self) -> Session | None:
        """Get the currently running session.

        Returns:
            The running Session if any, None otherwise.
        """
        for session in self.sessions.values():
            if session.status == SessionStatus.RUNNING:
                return session
        return None
