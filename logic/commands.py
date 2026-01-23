"""Command definitions for fencing footwork training."""
from dataclasses import dataclass


@dataclass
class Command:
    """A fencing command with French and Japanese translations."""

    id: str
    french: str
    japanese: str
    audio_file: str
    is_weapon_specific: bool = False
    weapons: list[str] | None = None

    def to_dict(self) -> dict:
        """Convert to dict format for SSE events."""
        return {
            "id": self.id,
            "fr": self.french,
            "jp": self.japanese,
            "audio": f"/static/audio/{self.audio_file}",
        }


# All available fencing commands
COMMANDS: dict[str, Command] = {
    "en_garde": Command(
        id="en_garde",
        french="En garde",
        japanese="アンギャルド",
        audio_file="en_garde.mp3",
    ),
    "marche": Command(
        id="marche",
        french="Marchez",
        japanese="マルシェ",
        audio_file="marche.mp3",
    ),
    "rompe": Command(
        id="rompe",
        french="Rompez",
        japanese="ロンペ",
        audio_file="rompe.mp3",
    ),
    "allongez": Command(
        id="allongez",
        french="Allongez le bras",
        japanese="アロンジェ・ル・ブラ",
        audio_file="allongez.mp3",
    ),
    "fendez": Command(
        id="fendez",
        french="Fendez",
        japanese="ファンドゥ",
        audio_file="fendez.mp3",
    ),
    "remise": Command(
        id="remise",
        french="Remise en garde",
        japanese="ルミーズ・アンギャルド",
        audio_file="remise.mp3",
    ),
    "balancez": Command(
        id="balancez",
        french="Balancez",
        japanese="バランセ",
        audio_file="balancez.mp3",
    ),
    "double_marche": Command(
        id="double_marche",
        french="Double marchez",
        japanese="ドゥブル・マルシェ",
        audio_file="double_marche.mp3",
    ),
    "bond_avant": Command(
        id="bond_avant",
        french="Bond en avant",
        japanese="ボンナバン",
        audio_file="bond_avant.mp3",
    ),
    "bond_arriere": Command(
        id="bond_arriere",
        french="Bond en arrière",
        japanese="ボンナリエール",
        audio_file="bond_arriere.mp3",
    ),
    "fleche": Command(
        id="fleche",
        french="Flèche",
        japanese="フレッシュ",
        audio_file="fleche.mp3",
        is_weapon_specific=True,
        weapons=["sabre"],
    ),
    "halte": Command(
        id="halte",
        french="Halte",
        japanese="止め",
        audio_file="halte.mp3",
    ),
}

# Command sets for different skill levels
COMMAND_SETS: dict[str, list[str]] = {
    "beginner": ["marche", "rompe"],
    "intermediate": ["marche", "rompe", "fendez", "remise"],
    "advanced": ["marche", "rompe", "fendez", "remise", "bond_avant", "bond_arriere", "balancez"],
}

# Drill pairs for basic mode pair training
DRILL_PAIRS: dict[str, tuple[str, str]] = {
    "marche_rompe": ("marche", "rompe"),
    "en_garde_fendez": ("en_garde", "fendez"),
    "bond": ("bond_avant", "bond_arriere"),
    "allongez_fendez": ("allongez", "fendez"),
    "fendez_remise": ("fendez", "remise"),
}

# Position effects for each command (relative to initial en garde position)
# Positive values = forward (toward opponent), Negative = backward (away from opponent)
POSITION_EFFECTS: dict[str, float] = {
    "en_garde": 0.0,
    "marche": 1.0,
    "rompe": -1.0,
    "allongez": 0.0,
    "fendez": 2.0,
    "remise": -2.0,  # Return from lunge position
    "balancez": 0.0,
    "double_marche": 2.0,
    "bond_avant": 1.5,
    "bond_arriere": -1.5,
    "fleche": 3.0,
    "halte": 0.0,  # Stop command - no position change
}


def get_command(command_id: str) -> Command:
    """Get a command by its ID.

    Args:
        command_id: The command identifier.

    Returns:
        The Command object.

    Raises:
        KeyError: If the command ID is not found.
    """
    return COMMANDS[command_id]


def is_command_valid_for_weapon(command_id: str, weapon: str) -> bool:
    """Check if a command is valid for a given weapon.

    Args:
        command_id: The command identifier.
        weapon: The weapon type ('foil', 'epee', 'sabre').

    Returns:
        True if the command is valid for the weapon, False otherwise.
    """
    cmd = COMMANDS.get(command_id)
    if cmd is None:
        return False

    if not cmd.is_weapon_specific:
        # Non-weapon-specific commands are valid for all weapons
        return True

    # Weapon-specific commands are only valid for their allowed weapons
    return cmd.weapons is not None and weapon in cmd.weapons
