"""Command generation per training mode."""
import random
from typing import Optional

from logic.session import CombinationConfig, IntervalConfig


# Combination patterns as defined in plan.md
PATTERNS: dict[str, list[str]] = {
    # Pattern A (前進攻撃): マルシェ → マルシェ → アロンジェ・ル・ブラ → ファンドゥ → ルミーズ・アンギャルド
    "A": ["marche", "marche", "allongez", "fendez", "remise"],
    # Pattern B (後退からの反撃): ロンペ → ロンペ → マルシェ → ファンドゥ → ルミーズ・アンギャルド
    "B": ["rompe", "rompe", "marche", "fendez", "remise"],
    # Pattern C (フットワーク強化): マルシェ → マルシェ → ロンペ → マルシェ → ロンペ → ロンペ
    "C": ["marche", "marche", "rompe", "marche", "rompe", "rompe"],
}

# Direction classification for wall prevention
FORWARD_COMMANDS = {"marche", "double_marche", "bond_avant"}
BACKWARD_COMMANDS = {"rompe", "bond_arriere"}
BOND_COMMANDS = {"bond_avant", "bond_arriere"}

# Wall prevention threshold (avoid 5+ consecutive same-direction)
WALL_THRESHOLD = 4


def generate_combination(config: CombinationConfig) -> list[str]:
    """Generate command sequence for combination mode.

    Args:
        config: Combination mode configuration with pattern_id and repetitions.

    Returns:
        List of command IDs to execute.

    Raises:
        KeyError: If pattern_id is not found.
    """
    pattern = PATTERNS[config.pattern_id]
    return pattern * config.repetitions


def generate_interval_work_commands(config: IntervalConfig) -> list[str]:
    """Generate commands for a single work phase of interval mode.

    Uses intermediate command set for good variety without being too complex.

    Args:
        config: Interval mode configuration.

    Returns:
        List of command IDs for the work phase.
    """
    from logic.commands import COMMAND_SETS

    command_set = COMMAND_SETS["intermediate"]
    command_count = int(config.work_seconds * config.tempo_bpm / 60)

    commands = []
    history: list[str] = []
    last_cmd: Optional[str] = None

    for _ in range(command_count):
        cmd = select_constrained_command(command_set, history, last_cmd)
        commands.append(cmd)
        history.append(cmd)
        last_cmd = cmd

    return commands


def classify_command_direction(command_id: str) -> str:
    """Classify a command as forward, backward, or neutral.

    Args:
        command_id: The command identifier.

    Returns:
        One of "forward", "backward", or "neutral".
    """
    if command_id in FORWARD_COMMANDS:
        return "forward"
    elif command_id in BACKWARD_COMMANDS:
        return "backward"
    else:
        return "neutral"


def should_force_remise(last_command: str) -> bool:
    """Check if remise must be forced after the last command.

    Args:
        last_command: The previous command ID.

    Returns:
        True if fendez was the last command.
    """
    return last_command == "fendez"


def is_bond_command(command_id: str) -> bool:
    """Check if command is a bond (jump) command.

    Args:
        command_id: The command identifier.

    Returns:
        True if it's bond_avant or bond_arriere.
    """
    return command_id in BOND_COMMANDS


def count_consecutive_direction(history: list[str], direction: str) -> int:
    """Count consecutive commands in the same direction from the end of history.

    Args:
        history: List of previous command IDs.
        direction: The direction to count ("forward" or "backward").

    Returns:
        Number of consecutive commands in that direction at the end.
    """
    if not history:
        return 0

    count = 0
    for cmd in reversed(history):
        cmd_dir = classify_command_direction(cmd)
        if cmd_dir == direction:
            count += 1
        elif cmd_dir != "neutral":
            # Different direction ends the streak
            break
        # Neutral commands don't break the streak but don't count

    return count


def is_wall_risk(history: list[str], proposed_command: str) -> bool:
    """Check if selecting proposed_command would cause wall risk.

    Wall risk occurs when 4+ consecutive same-direction commands
    are followed by another in the same direction (would be 5+).

    Args:
        history: List of previous command IDs.
        proposed_command: The command being considered.

    Returns:
        True if this would exceed wall threshold.
    """
    proposed_dir = classify_command_direction(proposed_command)
    if proposed_dir == "neutral":
        return False

    consecutive = count_consecutive_direction(history, proposed_dir)
    return consecutive >= WALL_THRESHOLD


def select_constrained_command(
    command_set: list[str],
    history: list[str],
    last_command: Optional[str],
) -> str:
    """Select a command respecting all constraints.

    Constraints:
    1. Must be from command_set
    2. After fendez, must return remise
    3. Avoid wall risk (5+ consecutive same direction)

    Args:
        command_set: Available commands to select from.
        history: Previous commands for constraint checking.
        last_command: The immediately previous command (for fendez rule).

    Returns:
        Selected command ID.
    """
    # Rule 1: Fendez must be followed by remise
    if last_command and should_force_remise(last_command):
        return "remise"

    # Filter commands to avoid wall risk
    valid_commands = [
        cmd for cmd in command_set if not is_wall_risk(history, cmd)
    ]

    # Fallback: if all commands would cause wall risk, allow any
    if not valid_commands:
        valid_commands = command_set

    return random.choice(valid_commands)


def get_post_command_delay(command_id: str, base_delay: float) -> float:
    """Get the delay after a command (for bond commands, use longer delay).

    Args:
        command_id: The command identifier.
        base_delay: The base delay in seconds.

    Returns:
        Adjusted delay in seconds.
    """
    if is_bond_command(command_id):
        return base_delay * 1.5
    return base_delay
