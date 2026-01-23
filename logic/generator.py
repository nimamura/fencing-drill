"""Command generation per training mode."""
import random
from dataclasses import dataclass, field
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

# Command transition rules for natural movement flow
# Each command can specify preferred next commands with a probability
COMMAND_TRANSITIONS: dict[str, dict] = {
    "allongez": {
        "next_preferred": ["fendez"],
        "preferred_weight": 0.8,  # 80% chance of fendez after allongez
    },
    "balancez": {
        "next_preferred": ["marche", "fendez", "bond_avant"],
        "preferred_weight": 0.6,  # 60% chance of action after balancez
    },
}


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


def get_preferred_next_command(
    last_command: str,
    command_set: list[str],
) -> Optional[str]:
    """Get preferred next command based on transition rules.

    Args:
        last_command: The previous command ID.
        command_set: Available commands to select from.

    Returns:
        A preferred command ID if rule matches and command available,
        None otherwise.
    """
    if last_command not in COMMAND_TRANSITIONS:
        return None

    rule = COMMAND_TRANSITIONS[last_command]
    preferred = rule.get("next_preferred", [])
    weight = rule.get("preferred_weight", 0.5)

    # Filter to commands available in command_set
    available_preferred = [cmd for cmd in preferred if cmd in command_set]
    if not available_preferred:
        return None

    # Apply probability - return preferred command with specified probability
    if random.random() < weight:
        return random.choice(available_preferred)

    return None


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
    3. Apply command transition rules (e.g., allongez -> fendez)
    4. Avoid wall risk (5+ consecutive same direction)
    5. Respect weapon-specific command weights

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

    # Rule 2: Apply command transition rules
    if last_command:
        preferred = get_preferred_next_command(last_command, filtered_commands)
        if preferred:
            return preferred

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


# Position tracking constants
POSITION_SOFT_LIMIT = 3.0  # Beyond this, bias toward return
POSITION_HARD_LIMIT = 5.0  # Beyond this, force return direction


@dataclass
class PositionTracker:
    """Track fencer position relative to starting en garde position.

    Positive position = forward (toward opponent)
    Negative position = backward (away from opponent)
    """

    position: float = 0.0

    def apply_command(self, command_id: str) -> None:
        """Update position based on command executed.

        Args:
            command_id: The command that was executed.
        """
        from logic.commands import POSITION_EFFECTS

        effect = POSITION_EFFECTS.get(command_id, 0.0)
        self.position += effect

    def reset(self) -> None:
        """Reset position to initial en garde (position 0)."""
        self.position = 0.0

    def get_position_bias(self) -> str:
        """Get recommended movement direction based on current position.

        Returns:
            "forward" if far backward (should move forward)
            "backward" if far forward (should move backward)
            "neutral" if near starting position
        """
        if self.position > POSITION_SOFT_LIMIT:
            return "backward"
        elif self.position < -POSITION_SOFT_LIMIT:
            return "forward"
        return "neutral"


def generate_random_commands(
    command_set: str,
    count: int,
    weapon: str = "foil",
) -> list[str]:
    """Generate position-balanced random commands using phrases.

    Uses the phrase system to generate natural movement sequences
    while respecting position limits and weapon restrictions.

    Args:
        command_set: Difficulty level ("beginner", "intermediate", "advanced").
        count: Number of commands to generate.
        weapon: Weapon type for filtering.

    Returns:
        List of command IDs.
    """
    from logic.phrases import get_phrases_for_difficulty, select_balanced_phrase
    from logic.commands import COMMAND_SETS

    # Get available phrases for difficulty
    phrases = get_phrases_for_difficulty(command_set)

    # Track position
    tracker = PositionTracker()

    # Collect commands
    commands: list[str] = []
    last_cmd: Optional[str] = None

    # Get actual command set for constraint checking
    actual_command_set = COMMAND_SETS.get(command_set, COMMAND_SETS["beginner"])

    while len(commands) < count:
        # Select a phrase based on current position
        phrase = select_balanced_phrase(tracker.position, phrases)

        # Generate commands from phrase, respecting constraints
        for cmd in phrase.commands:
            if len(commands) >= count:
                break

            # Apply fendez->remise rule
            if last_cmd and should_force_remise(last_cmd):
                cmd = "remise"

            # Skip consecutive remise (never allow remise after remise)
            if cmd == "remise" and last_cmd == "remise":
                continue

            # Apply command transition rules (except when fendez->remise forced)
            elif last_cmd and last_cmd != "fendez":
                preferred = get_preferred_next_command(last_cmd, actual_command_set)
                if preferred and preferred in actual_command_set:
                    cmd = preferred

            # Skip commands not in command set (for difficulty filtering)
            if cmd not in actual_command_set:
                continue

            # Apply weapon filtering
            from logic.weapons import get_weapon_profile
            profile = get_weapon_profile(weapon)

            # Skip if command is filtered out by weapon
            if cmd in profile.command_weights and profile.command_weights[cmd] == 0.0:
                continue

            # Check weapon-specific commands
            from logic.commands import COMMANDS
            cmd_obj = COMMANDS.get(cmd)
            if cmd_obj and cmd_obj.is_weapon_specific:
                if cmd_obj.weapons and weapon not in cmd_obj.weapons:
                    continue

            commands.append(cmd)
            tracker.apply_command(cmd)
            last_cmd = cmd

    return commands
