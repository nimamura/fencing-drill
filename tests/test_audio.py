"""Tests for audio files and playback integration."""
import os
from pathlib import Path

import pytest

from logic.commands import COMMANDS

# Path to audio directory
AUDIO_DIR = Path(__file__).parent.parent / "static" / "audio"


class TestAudioFilesExist:
    """Test that all required audio files exist."""

    def test_audio_directory_exists(self):
        """Audio directory should exist."""
        assert AUDIO_DIR.exists()
        assert AUDIO_DIR.is_dir()

    @pytest.mark.parametrize("command_id", list(COMMANDS.keys()))
    def test_command_audio_file_exists(self, command_id):
        """Each command should have a corresponding audio file."""
        command = COMMANDS[command_id]
        audio_path = AUDIO_DIR / command.audio_file
        assert audio_path.exists(), f"Missing audio file: {command.audio_file}"

    def test_repos_audio_exists(self):
        """Rest (repos) audio file should exist for interval mode."""
        audio_path = AUDIO_DIR / "repos.mp3"
        assert audio_path.exists(), "Missing audio file: repos.mp3"

    def test_termine_audio_exists(self):
        """End (termine) audio file should exist."""
        audio_path = AUDIO_DIR / "termine.mp3"
        assert audio_path.exists(), "Missing audio file: termine.mp3"


class TestAudioFilesValid:
    """Test that audio files are valid."""

    @pytest.mark.parametrize("command_id", list(COMMANDS.keys()))
    def test_command_audio_file_not_empty(self, command_id):
        """Each command audio file should not be empty."""
        command = COMMANDS[command_id]
        audio_path = AUDIO_DIR / command.audio_file
        assert audio_path.stat().st_size > 0, f"Empty audio file: {command.audio_file}"

    @pytest.mark.parametrize("command_id", list(COMMANDS.keys()))
    def test_command_audio_file_is_mp3(self, command_id):
        """Each command audio file should be an MP3 file."""
        command = COMMANDS[command_id]
        audio_path = AUDIO_DIR / command.audio_file

        # Check file extension
        assert audio_path.suffix == ".mp3", f"Audio file not MP3: {command.audio_file}"

        # Check MP3 header (ID3 or sync bytes)
        with open(audio_path, "rb") as f:
            header = f.read(3)
            # MP3 files start with ID3 tag or sync bytes (0xFF 0xFB/FA/F3/F2)
            is_id3 = header == b"ID3"
            is_sync = header[0:2] == b"\xff\xfb" or header[0:2] == b"\xff\xfa"
            assert is_id3 or is_sync or header[0] == 0xff, (
                f"Invalid MP3 header in {command.audio_file}"
            )

    def test_repos_audio_is_valid_mp3(self):
        """Rest audio file should be a valid MP3."""
        audio_path = AUDIO_DIR / "repos.mp3"
        assert audio_path.stat().st_size > 0
        with open(audio_path, "rb") as f:
            header = f.read(3)
            is_id3 = header == b"ID3"
            is_sync = header[0] == 0xff
            assert is_id3 or is_sync, "Invalid MP3 header in repos.mp3"


class TestAudioFileReferences:
    """Test that code references valid audio files."""

    def test_command_audio_paths_are_relative(self):
        """Command audio paths should be relative filenames, not absolute paths."""
        for command_id, command in COMMANDS.items():
            assert not command.audio_file.startswith("/"), (
                f"Audio path should be relative: {command.audio_file}"
            )
            assert "/" not in command.audio_file, (
                f"Audio path should be filename only: {command.audio_file}"
            )

    def test_command_to_dict_has_full_audio_path(self):
        """Command.to_dict() should include full audio URL path."""
        for command_id, command in COMMANDS.items():
            data = command.to_dict()
            assert "audio" in data
            assert data["audio"].startswith("/static/audio/")
            assert data["audio"].endswith(".mp3")


class TestIntervalModeAudio:
    """Test audio files needed for interval mode."""

    def test_countdown_audio_files_exist(self):
        """Countdown audio files (3, 2, 1) should exist."""
        for num in ["trois", "deux", "un"]:
            audio_path = AUDIO_DIR / f"{num}.mp3"
            assert audio_path.exists(), f"Missing countdown audio: {num}.mp3"

    def test_allez_audio_exists(self):
        """Allez (go) audio should exist for interval mode."""
        audio_path = AUDIO_DIR / "allez.mp3"
        assert audio_path.exists(), "Missing audio file: allez.mp3"

    def test_halte_audio_exists(self):
        """Halte (stop) audio should exist."""
        audio_path = AUDIO_DIR / "halte.mp3"
        assert audio_path.exists(), "Missing audio file: halte.mp3"

    def test_pret_audio_exists(self):
        """Pret (ready) audio should exist."""
        audio_path = AUDIO_DIR / "pret.mp3"
        assert audio_path.exists(), "Missing audio file: pret.mp3"


class TestTimingCalculations:
    """Test timing calculations for audio playback."""

    def test_basic_mode_interval_calculation(self):
        """Basic mode should calculate interval from BPM."""
        # 60 BPM = 1 command per second = 1.0s interval
        tempo_bpm = 60
        interval = 60.0 / tempo_bpm
        assert interval == 1.0

        # 120 BPM = 2 commands per second = 0.5s interval
        tempo_bpm = 120
        interval = 60.0 / tempo_bpm
        assert interval == 0.5

        # 30 BPM = 0.5 commands per second = 2.0s interval
        tempo_bpm = 30
        interval = 60.0 / tempo_bpm
        assert interval == 2.0

    def test_random_mode_interval_range(self):
        """Random mode should have configurable interval range."""
        from logic.session import RandomConfig

        config = RandomConfig(
            command_set="beginner",
            duration_seconds=60,
            min_interval_ms=500,
            max_interval_ms=2000,
        )

        assert config.min_interval_ms == 500
        assert config.max_interval_ms == 2000

        # Convert to seconds for sleep
        min_secs = config.min_interval_ms / 1000.0
        max_secs = config.max_interval_ms / 1000.0
        assert min_secs == 0.5
        assert max_secs == 2.0

    def test_interval_mode_work_interval(self):
        """Interval mode should calculate work interval from BPM."""
        from logic.session import IntervalConfig

        config = IntervalConfig(
            work_seconds=30,
            rest_seconds=15,
            sets=5,
            tempo_bpm=90,
        )

        work_interval = 60.0 / config.tempo_bpm
        # 90 BPM = 1.5 commands per second = 0.667s interval
        assert abs(work_interval - 0.667) < 0.01
