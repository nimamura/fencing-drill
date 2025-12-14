"""Tests for logic/commands.py - Command definitions."""
import pytest


class TestCommand:
    """Test the Command dataclass."""

    def test_command_has_required_fields(self):
        """Command should have id, french, japanese, and audio_file fields."""
        from logic.commands import Command

        cmd = Command(
            id="marche",
            french="Marchez",
            japanese="マルシェ",
            audio_file="marche.mp3",
        )

        assert cmd.id == "marche"
        assert cmd.french == "Marchez"
        assert cmd.japanese == "マルシェ"
        assert cmd.audio_file == "marche.mp3"

    def test_command_to_dict(self):
        """Command should be convertible to dict for SSE events."""
        from logic.commands import Command

        cmd = Command(
            id="marche",
            french="Marchez",
            japanese="マルシェ",
            audio_file="marche.mp3",
        )

        result = cmd.to_dict()

        assert result == {
            "id": "marche",
            "fr": "Marchez",
            "jp": "マルシェ",
            "audio": "/static/audio/marche.mp3",
        }


class TestCommands:
    """Test the COMMANDS dictionary."""

    def test_commands_contains_all_basic_commands(self):
        """COMMANDS should contain all basic fencing commands."""
        from logic.commands import COMMANDS

        required_commands = [
            "en_garde",
            "marche",
            "rompe",
            "allongez",
            "fendez",
            "remise",
            "balancez",
            "double_marche",
            "bond_avant",
            "bond_arriere",
        ]

        for cmd_id in required_commands:
            assert cmd_id in COMMANDS, f"Missing command: {cmd_id}"

    def test_en_garde_command(self):
        """En garde command should have correct French and Japanese."""
        from logic.commands import COMMANDS

        cmd = COMMANDS["en_garde"]
        assert cmd.french == "En garde"
        assert cmd.japanese == "アンギャルド"

    def test_marche_command(self):
        """Marche command should have correct French and Japanese."""
        from logic.commands import COMMANDS

        cmd = COMMANDS["marche"]
        assert cmd.french == "Marchez"
        assert cmd.japanese == "マルシェ"

    def test_rompe_command(self):
        """Rompe command should have correct French and Japanese."""
        from logic.commands import COMMANDS

        cmd = COMMANDS["rompe"]
        assert cmd.french == "Rompez"
        assert cmd.japanese == "ロンペ"

    def test_fendez_command(self):
        """Fendez command should have correct French and Japanese."""
        from logic.commands import COMMANDS

        cmd = COMMANDS["fendez"]
        assert cmd.french == "Fendez"
        assert cmd.japanese == "ファンドゥ"

    def test_remise_command(self):
        """Remise command should have correct French and Japanese."""
        from logic.commands import COMMANDS

        cmd = COMMANDS["remise"]
        assert cmd.french == "Remise en garde"
        assert cmd.japanese == "ルミーズ・アンギャルド"


class TestCommandSets:
    """Test command sets for different levels."""

    def test_beginner_commands(self):
        """Beginner commands should contain only marche and rompe."""
        from logic.commands import COMMAND_SETS

        beginner = COMMAND_SETS["beginner"]
        assert "marche" in beginner
        assert "rompe" in beginner
        assert len(beginner) == 2

    def test_intermediate_commands(self):
        """Intermediate commands should include beginner + fendez, remise."""
        from logic.commands import COMMAND_SETS

        intermediate = COMMAND_SETS["intermediate"]
        assert "marche" in intermediate
        assert "rompe" in intermediate
        assert "fendez" in intermediate
        assert "remise" in intermediate
        assert len(intermediate) == 4

    def test_advanced_commands(self):
        """Advanced commands should include intermediate + bond_avant, bond_arriere, balancez."""
        from logic.commands import COMMAND_SETS

        advanced = COMMAND_SETS["advanced"]
        assert "marche" in advanced
        assert "rompe" in advanced
        assert "fendez" in advanced
        assert "remise" in advanced
        assert "bond_avant" in advanced
        assert "bond_arriere" in advanced
        assert "balancez" in advanced
        assert len(advanced) == 7


class TestGetCommand:
    """Test get_command helper function."""

    def test_get_existing_command(self):
        """get_command should return Command for valid id."""
        from logic.commands import get_command, Command

        cmd = get_command("marche")
        assert isinstance(cmd, Command)
        assert cmd.id == "marche"

    def test_get_nonexistent_command(self):
        """get_command should raise KeyError for invalid id."""
        from logic.commands import get_command

        with pytest.raises(KeyError):
            get_command("invalid_command")
