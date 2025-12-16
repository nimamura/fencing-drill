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
    weapon: str = "foil",
) -> str:
    """Select a command respecting all constraints and weapon filtering.

    Constraints:
    1. Must be from command_set (filtered by weapon)
    2. After fendez, must return remise
    3. Avoid wall risk (5+ consecutive same direction)
    4. Respect weapon-specific command weights

    Args:
        command_set: Available commands to select from.
        history: Previous commands for constraint checking.
        last_command: The immediately previous command (for fendez rule).
        weapon: Weapon type for filtering ('foil', 'epee', 'sabre').

    Returns:
        Selected command ID.
    """
    from logic.weapons import get_weapon_profile

    # Rule 1: Fendez must be followed by remise
    if last_command and should_force_remise(last_command):
        return "remise"

    # Apply weapon filtering
    profile = get_weapon_profile(weapon)
    filtered_commands = filter_commands_for_weapon(command_set, weapon, profile)
    weighted_commands = apply_weapon_weights(filtered_commands, profile.command_weights)

    # Filter out wall risk commands
    safe_weighted = [
        (cmd, weight) for cmd, weight in weighted_commands
        if not is_wall_risk(history, cmd)
    ]

    # Fallback: if all commands would cause wall risk, use all weighted commands
    if not safe_weighted:
        safe_weighted = weighted_commands

    # Fallback: if weighted_commands is empty (all commands filtered out)
    # Apply weights to original command_set (preserves weapon filtering)
    if not safe_weighted:
        fallback_weighted = apply_weapon_weights(command_set, profile.command_weights)
        if fallback_weighted:
            return select_weighted_command(fallback_weighted)
        # Ultimate fallback - this shouldn't happen normally
        return random.choice(command_set)

    return select_weighted_command(safe_weighted)


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


def filter_commands_for_weapon(
    command_ids: list[str],
    weapon: str,
    profile: "WeaponProfile",
) -> list[str]:
    """Filter commands based on weapon restrictions and add weapon-specific commands.

    Args:
        command_ids: List of command IDs to filter.
        weapon: The weapon type string ('foil', 'epee', or 'sabre').
        profile: The weapon profile with additional_commands.

    Returns:
        Filtered list of command IDs.
    """
    from logic.commands import COMMANDS

    result = []

    for cmd_id in command_ids:
        cmd = COMMANDS.get(cmd_id)
        if cmd is None:
            continue

        if cmd.is_weapon_specific:
            # Only include if this weapon is allowed
            if cmd.weapons and weapon in cmd.weapons:
                result.append(cmd_id)
        else:
            # Non-weapon-specific commands are always included
            result.append(cmd_id)

    # Add weapon-specific additional commands
    for cmd_id in profile.additional_commands:
        if cmd_id not in result:
            result.append(cmd_id)

    return result


def apply_weapon_weights(
    command_ids: list[str],
    weights: dict[str, float],
) -> list[tuple[str, float]]:
    """Apply weapon-specific weights to commands.

    Args:
        command_ids: List of command IDs.
        weights: Dict mapping command_id to weight (default 1.0, 0.0 = excluded).

    Returns:
        List of (command_id, weight) tuples, excluding zero-weight commands.
    """
    result = []

    for cmd_id in command_ids:
        weight = weights.get(cmd_id, 1.0)
        if weight > 0:
            result.append((cmd_id, weight))

    return result


def select_weighted_command(weighted_commands: list[tuple[str, float]]) -> str:
    """Select a command using weighted random choice.

    Args:
        weighted_commands: List of (command_id, weight) tuples.

    Returns:
        Selected command ID.

    Raises:
        ValueError: If weighted_commands is empty.
    """
    if not weighted_commands:
        raise ValueError("No commands available for selection")

    commands, weights = zip(*weighted_commands)
    return random.choices(commands, weights=weights, k=1)[0]
