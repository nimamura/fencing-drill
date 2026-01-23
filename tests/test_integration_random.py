"""Integration tests for phrase-based random command generation."""
import json
import pytest
import random


class TestPhraseBasedRandomGeneration:
    """Test the complete phrase-based random generation flow."""

    def test_generate_random_commands_returns_list(self):
        """generate_random_commands should return a list of command IDs."""
        from logic.generator import generate_random_commands

        commands = generate_random_commands(
            command_set="intermediate",
            count=20,
        )

        assert isinstance(commands, list)
        assert len(commands) == 20

    def test_generate_random_commands_all_valid(self):
        """All generated commands should be valid command IDs."""
        from logic.generator import generate_random_commands
        from logic.commands import COMMANDS

        commands = generate_random_commands(
            command_set="intermediate",
            count=50,
        )

        for cmd in commands:
            assert cmd in COMMANDS, f"Invalid command: {cmd}"

    def test_random_commands_stay_within_position_limits(self):
        """Generated commands should keep position within limits."""
        from logic.generator import generate_random_commands, POSITION_HARD_LIMIT
        from logic.commands import POSITION_EFFECTS

        random.seed(42)

        # Generate many commands and track position
        commands = generate_random_commands(
            command_set="advanced",
            count=200,
        )

        position = 0.0
        max_position = 0.0
        min_position = 0.0

        for cmd in commands:
            position += POSITION_EFFECTS.get(cmd, 0.0)
            max_position = max(max_position, position)
            min_position = min(min_position, position)

        # Position should stay within reasonable bounds
        # Allow some margin beyond hard limit for phrase completion
        limit_with_margin = POSITION_HARD_LIMIT + 3.0
        assert max_position <= limit_with_margin, (
            f"Max position {max_position} exceeded limit {limit_with_margin}"
        )
        assert min_position >= -limit_with_margin, (
            f"Min position {min_position} exceeded limit {-limit_with_margin}"
        )

    def test_random_commands_fendez_followed_by_remise(self):
        """Fendez should always be followed by remise."""
        from logic.generator import generate_random_commands

        random.seed(42)

        commands = generate_random_commands(
            command_set="intermediate",
            count=100,
        )

        for i, cmd in enumerate(commands):
            if cmd == "fendez" and i + 1 < len(commands):
                assert commands[i + 1] == "remise", (
                    f"fendez at index {i} not followed by remise"
                )

    def test_random_commands_allongez_prefers_fendez(self):
        """allongez should frequently be followed by fendez."""
        from logic.generator import generate_random_commands

        random.seed(42)

        commands = generate_random_commands(
            command_set="intermediate",
            count=500,
        )

        allongez_count = 0
        allongez_fendez_count = 0

        for i, cmd in enumerate(commands):
            if cmd == "allongez" and i + 1 < len(commands):
                allongez_count += 1
                if commands[i + 1] == "fendez":
                    allongez_fendez_count += 1

        if allongez_count > 0:
            ratio = allongez_fendez_count / allongez_count
            # Should be around 80% (allow 60-95% range)
            assert 0.6 < ratio < 0.95, (
                f"allongez->fendez ratio {ratio:.1%} outside expected range"
            )


class TestPhraseBasedRandomDifficulty:
    """Test difficulty-based phrase selection."""

    def test_beginner_uses_only_basic_commands(self):
        """Beginner command set should only use marche/rompe."""
        from logic.generator import generate_random_commands

        commands = generate_random_commands(
            command_set="beginner",
            count=50,
        )

        allowed = {"marche", "rompe"}
        for cmd in commands:
            assert cmd in allowed, f"Beginner got non-basic command: {cmd}"

    def test_intermediate_includes_fendez_remise(self):
        """Intermediate command set should include fendez/remise."""
        from logic.generator import generate_random_commands

        random.seed(42)

        commands = generate_random_commands(
            command_set="intermediate",
            count=100,
        )

        has_fendez = any(cmd == "fendez" for cmd in commands)
        assert has_fendez, "Intermediate should include fendez"

    def test_advanced_includes_bonds(self):
        """Advanced command set should include bond commands."""
        from logic.generator import generate_random_commands

        random.seed(42)

        commands = generate_random_commands(
            command_set="advanced",
            count=200,
        )

        has_bond = any(cmd in ("bond_avant", "bond_arriere") for cmd in commands)
        assert has_bond, "Advanced should include bond commands"


class TestPhraseBasedRandomWeapon:
    """Test weapon-specific behavior in phrase-based generation."""

    def test_sabre_excludes_balancez(self):
        """Sabre should never generate balancez commands."""
        from logic.generator import generate_random_commands

        random.seed(42)

        commands = generate_random_commands(
            command_set="advanced",
            count=200,
            weapon="sabre",
        )

        assert "balancez" not in commands, "Sabre should not use balancez"

    def test_foil_excludes_fleche(self):
        """Foil should never generate fleche commands."""
        from logic.generator import generate_random_commands

        random.seed(42)

        commands = generate_random_commands(
            command_set="advanced",
            count=200,
            weapon="foil",
        )

        assert "fleche" not in commands, "Foil should not use fleche"


class TestRemiseConstraints:
    """Test remise-specific constraints in random generation."""

    def test_no_consecutive_remise(self):
        """Remise should never appear consecutively."""
        from logic.generator import generate_random_commands

        random.seed(42)

        # Generate many commands to ensure statistical coverage
        commands = generate_random_commands(
            command_set="intermediate",
            count=500,
        )

        # Check for consecutive remise
        for i in range(len(commands) - 1):
            if commands[i] == "remise":
                assert commands[i + 1] != "remise", (
                    f"Found consecutive remise at index {i} and {i + 1}"
                )

    def test_remise_frequency_within_limit(self):
        """Remise should not exceed 25% of all commands."""
        from logic.generator import generate_random_commands

        random.seed(42)

        # Generate many commands for statistical significance
        commands = generate_random_commands(
            command_set="intermediate",
            count=500,
        )

        remise_count = sum(1 for cmd in commands if cmd == "remise")
        remise_ratio = remise_count / len(commands)

        # Remise should not exceed 25%
        assert remise_ratio <= 0.25, (
            f"Remise frequency {remise_ratio:.1%} exceeds 25% limit "
            f"({remise_count} out of {len(commands)})"
        )


class TestSessionEndSignal:
    """Test session end signal with halte command."""

    def test_halte_command_exists(self):
        """Halte command should be defined in COMMANDS."""
        from logic.commands import COMMANDS

        assert "halte" in COMMANDS, "halte command should exist"
        halte = COMMANDS["halte"]
        assert halte.french == "Halte"
        assert halte.audio_file == "halte.mp3"

    @pytest.mark.asyncio
    async def test_session_ends_with_halte(self):
        """Session should send halte command before end event."""
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)

        # Start a basic session with minimal repetitions
        response = client.post(
            "/session/start",
            data={
                "mode": "basic",
                "pair_id": "marche_rompe",
                "repetitions": 2,
                "tempo_bpm": 120,  # Fast tempo for quick test
                "weapon": "foil",
            },
        )
        assert response.status_code == 200

        # Extract session_id from response
        import re
        match = re.search(r'data-session-id="([^"]+)"', response.text)
        assert match, "Session ID not found in response"
        session_id = match.group(1)

        # Collect events from SSE stream
        events = []
        with client.stream("GET", f"/session/stream?session_id={session_id}") as sse:
            for line in sse.iter_lines():
                if line.startswith("event:"):
                    event_type = line.split(":", 1)[1].strip()
                elif line.startswith("data:"):
                    data = line.split(":", 1)[1].strip()
                    events.append({"event": event_type, "data": json.loads(data)})
                    if event_type == "end":
                        break

        # Find the last command before end event
        command_events = [e for e in events if e["event"] == "command"]
        assert len(command_events) >= 2, "Should have at least 2 command events"

        # The last command before 'end' should be 'halte'
        last_command = command_events[-1]["data"]
        assert last_command["id"] == "halte", (
            f"Last command should be 'halte', got '{last_command['id']}'"
        )
