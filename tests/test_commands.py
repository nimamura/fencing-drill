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


class TestCommandWeaponFields:
    """Test weapon-specific fields on Command."""

    def test_command_default_not_weapon_specific(self):
        """Commands should default to is_weapon_specific=False."""
        from logic.commands import Command

        cmd = Command(
            id="test",
            french="Test",
            japanese="テスト",
            audio_file="test.mp3",
        )

        assert cmd.is_weapon_specific is False

    def test_command_default_weapons_none(self):
        """Commands should default to weapons=None (all weapons)."""
        from logic.commands import Command

        cmd = Command(
            id="test",
            french="Test",
            japanese="テスト",
            audio_file="test.mp3",
        )

        assert cmd.weapons is None

    def test_command_weapon_specific_explicit(self):
        """Commands can be explicitly set as weapon-specific."""
        from logic.commands import Command

        cmd = Command(
            id="fleche",
            french="Flèche",
            japanese="フレッシュ",
            audio_file="fleche.mp3",
            is_weapon_specific=True,
            weapons=["sabre"],
        )

        assert cmd.is_weapon_specific is True
        assert cmd.weapons == ["sabre"]

    def test_fleche_is_weapon_specific(self):
        """Fleche command should have is_weapon_specific=True."""
        from logic.commands import COMMANDS

        cmd = COMMANDS["fleche"]
        assert cmd.is_weapon_specific is True

    def test_fleche_weapons_sabre_only(self):
        """Fleche command should have weapons=['sabre']."""
        from logic.commands import COMMANDS

        cmd = COMMANDS["fleche"]
        assert cmd.weapons == ["sabre"]

    def test_marche_not_weapon_specific(self):
        """Marche should work for all weapons (is_weapon_specific=False)."""
        from logic.commands import COMMANDS

        cmd = COMMANDS["marche"]
        assert cmd.is_weapon_specific is False
        assert cmd.weapons is None


class TestIsCommandValidForWeapon:
    """Test is_command_valid_for_weapon function."""

    def test_non_weapon_specific_valid_for_all(self):
        """Non-weapon-specific commands are valid for all weapons."""
        from logic.commands import is_command_valid_for_weapon

        assert is_command_valid_for_weapon("marche", "foil") is True
        assert is_command_valid_for_weapon("marche", "epee") is True
        assert is_command_valid_for_weapon("marche", "sabre") is True

    def test_fleche_valid_for_sabre(self):
        """Fleche is valid for sabre."""
        from logic.commands import is_command_valid_for_weapon

        assert is_command_valid_for_weapon("fleche", "sabre") is True

    def test_fleche_invalid_for_foil(self):
        """Fleche is not valid for foil."""
        from logic.commands import is_command_valid_for_weapon

        assert is_command_valid_for_weapon("fleche", "foil") is False

    def test_fleche_invalid_for_epee(self):
        """Fleche is not valid for epee."""
        from logic.commands import is_command_valid_for_weapon

        assert is_command_valid_for_weapon("fleche", "epee") is False

    def test_nonexistent_command_invalid(self):
        """Nonexistent commands are invalid."""
        from logic.commands import is_command_valid_for_weapon

        assert is_command_valid_for_weapon("nonexistent", "foil") is False


class TestDrillPairs:
    """Test DRILL_PAIRS for basic mode pair training."""

    def test_drill_pairs_contains_all_pairs(self):
        """DRILL_PAIRS should contain all 5 training pairs."""
        from logic.commands import DRILL_PAIRS

        expected_pairs = [
            "marche_rompe",
            "en_garde_fendez",
            "bond",
            "allongez_fendez",
            "fendez_remise",
        ]

        for pair_id in expected_pairs:
            assert pair_id in DRILL_PAIRS, f"Missing pair: {pair_id}"

    def test_drill_pairs_are_tuples(self):
        """Each drill pair should be a tuple of two command IDs."""
        from logic.commands import DRILL_PAIRS

        for pair_id, pair in DRILL_PAIRS.items():
            assert isinstance(pair, tuple), f"{pair_id} should be a tuple"
            assert len(pair) == 2, f"{pair_id} should have exactly 2 commands"

    def test_drill_pairs_reference_valid_commands(self):
        """All commands in DRILL_PAIRS should exist in COMMANDS."""
        from logic.commands import DRILL_PAIRS, COMMANDS

        for pair_id, (cmd1, cmd2) in DRILL_PAIRS.items():
            assert cmd1 in COMMANDS, f"{pair_id}: {cmd1} not in COMMANDS"
            assert cmd2 in COMMANDS, f"{pair_id}: {cmd2} not in COMMANDS"

    def test_marche_rompe_pair(self):
        """marche_rompe pair should be (marche, rompe)."""
        from logic.commands import DRILL_PAIRS

        assert DRILL_PAIRS["marche_rompe"] == ("marche", "rompe")

    def test_en_garde_fendez_pair(self):
        """en_garde_fendez pair should be (en_garde, fendez)."""
        from logic.commands import DRILL_PAIRS

        assert DRILL_PAIRS["en_garde_fendez"] == ("en_garde", "fendez")

    def test_bond_pair(self):
        """bond pair should be (bond_avant, bond_arriere)."""
        from logic.commands import DRILL_PAIRS

        assert DRILL_PAIRS["bond"] == ("bond_avant", "bond_arriere")

    def test_allongez_fendez_pair(self):
        """allongez_fendez pair should be (allongez, fendez)."""
        from logic.commands import DRILL_PAIRS

        assert DRILL_PAIRS["allongez_fendez"] == ("allongez", "fendez")

    def test_fendez_remise_pair(self):
        """fendez_remise pair should be (fendez, remise)."""
        from logic.commands import DRILL_PAIRS

        assert DRILL_PAIRS["fendez_remise"] == ("fendez", "remise")
