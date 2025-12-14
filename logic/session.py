"""Session state management for training sessions."""
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Union


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

    command_id: str = "marche"
    repetitions: int = 10
    tempo_bpm: int = 60


@dataclass
class CombinationConfig:
    """Configuration for Combination training mode."""

    pattern_id: str = "A"
    repetitions: int = 5
    tempo_bpm: int = 60


@dataclass
class RandomConfig:
    """Configuration for Random training mode."""

    command_set: str = "beginner"
    duration_seconds: int = 60
    min_interval_ms: int = 1000
    max_interval_ms: int = 3000


@dataclass
class IntervalConfig:
    """Configuration for Interval training mode."""

    work_seconds: int = 30
    rest_seconds: int = 15
    sets: int = 5
    tempo_bpm: int = 90


# Type alias for any config type
SessionConfig = Union[BasicConfig, CombinationConfig, RandomConfig, IntervalConfig]


@dataclass
class Session:
    """A training session."""

    mode: TrainingMode
    config: SessionConfig
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: SessionStatus = SessionStatus.IDLE

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


class SessionManager:
    """Manages training sessions."""

    def __init__(self) -> None:
        self.sessions: dict[str, Session] = {}

    def create_session(
        self, mode: TrainingMode, config: SessionConfig
    ) -> Session:
        """Create a new training session.

        Args:
            mode: The training mode.
            config: The configuration for the mode.

        Returns:
            The created Session.
        """
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
