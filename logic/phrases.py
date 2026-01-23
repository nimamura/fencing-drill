"""Phrase-based command generation for natural movement sequences."""
import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class Phrase:
    """A meaningful sequence of fencing commands.

    Phrases represent natural movement patterns that a fencer would
    perform in training or competition.
    """

    id: str
    name: str
    commands: list[str]
    net_movement: float  # Total position change after phrase
    difficulty: str  # "beginner", "intermediate", "advanced"
    weight: float = 1.0  # Selection weight (0.5 for attack phrases with remise)


# Predefined phrases for different training scenarios
PHRASES: dict[str, Phrase] = {
    # Beginner phrases (marche/rompe only)
    "simple_advance": Phrase(
        id="simple_advance",
        name="Simple Advance",
        commands=["marche", "marche"],
        net_movement=2.0,
        difficulty="beginner",
    ),
    "simple_retreat": Phrase(
        id="simple_retreat",
        name="Simple Retreat",
        commands=["rompe", "rompe"],
        net_movement=-2.0,
        difficulty="beginner",
    ),
    "footwork_basic": Phrase(
        id="footwork_basic",
        name="Basic Footwork",
        commands=["marche", "rompe", "marche", "rompe"],
        net_movement=0.0,
        difficulty="beginner",
    ),
    # Intermediate phrases (includes fendez/remise)
    "advance_attack": Phrase(
        id="advance_attack",
        name="Advance Attack",
        commands=["marche", "marche", "fendez", "remise"],
        net_movement=2.0,  # 1 + 1 + 2 - 2 = 2
        difficulty="intermediate",
        weight=0.5,  # Reduced weight to lower remise frequency
    ),
    "retreat_counter": Phrase(
        id="retreat_counter",
        name="Retreat Counter",
        commands=["rompe", "rompe", "marche", "fendez", "remise"],
        net_movement=-1.0,  # -1 - 1 + 1 + 2 - 2 = -1
        difficulty="intermediate",
        weight=0.5,  # Reduced weight to lower remise frequency
    ),
    "prep_attack": Phrase(
        id="prep_attack",
        name="Prep Attack",
        commands=["allongez", "fendez", "remise"],
        net_movement=0.0,  # 0 + 2 - 2 = 0
        difficulty="intermediate",
        weight=0.5,  # Reduced weight to lower remise frequency
    ),
    "distance_adjust": Phrase(
        id="distance_adjust",
        name="Distance Adjust",
        commands=["marche", "marche", "rompe"],
        net_movement=1.0,
        difficulty="intermediate",
    ),
    "retreat_distance": Phrase(
        id="retreat_distance",
        name="Retreat Distance",
        commands=["rompe", "rompe", "marche"],
        net_movement=-1.0,
        difficulty="intermediate",
    ),
    # Advanced phrases (includes bonds)
    "bond_drill": Phrase(
        id="bond_drill",
        name="Bond Drill",
        commands=["bond_avant", "bond_arriere"],
        net_movement=0.0,  # 1.5 - 1.5 = 0
        difficulty="advanced",
    ),
    "aggressive_advance": Phrase(
        id="aggressive_advance",
        name="Aggressive Advance",
        commands=["bond_avant", "marche", "fendez", "remise"],
        net_movement=2.5,  # 1.5 + 1 + 2 - 2 = 2.5
        difficulty="advanced",
        weight=0.5,  # Reduced weight to lower remise frequency
    ),
    "defensive_retreat": Phrase(
        id="defensive_retreat",
        name="Defensive Retreat",
        commands=["bond_arriere", "rompe", "rompe"],
        net_movement=-3.5,  # -1.5 - 1 - 1 = -3.5
        difficulty="advanced",
    ),
    "balancez_attack": Phrase(
        id="balancez_attack",
        name="Balancez Attack",
        commands=["balancez", "marche", "fendez", "remise"],
        net_movement=1.0,  # 0 + 1 + 2 - 2 = 1
        difficulty="advanced",
        weight=0.5,  # Reduced weight to lower remise frequency
    ),
}


def get_phrases_for_difficulty(difficulty: str) -> list[Phrase]:
    """Get phrases available for a given difficulty level.

    Args:
        difficulty: The difficulty level ("beginner", "intermediate", "advanced").

    Returns:
        List of available Phrase objects for that level.
    """
    valid_difficulties = {"beginner", "intermediate", "advanced"}

    if difficulty not in valid_difficulties:
        difficulty = "beginner"

    if difficulty == "beginner":
        return [p for p in PHRASES.values() if p.difficulty == "beginner"]
    elif difficulty == "intermediate":
        return [p for p in PHRASES.values() if p.difficulty in ("beginner", "intermediate")]
    else:  # advanced
        return list(PHRASES.values())


def select_balanced_phrase(
    position: float,
    available_phrases: list[Phrase],
) -> Phrase:
    """Select a phrase considering current position for balance.

    Uses position-aware weighting to keep fencer near starting position.

    Args:
        position: Current position (positive = forward, negative = backward).
        available_phrases: List of phrases to choose from.

    Returns:
        Selected Phrase.

    Raises:
        ValueError: If available_phrases is empty.
    """
    from logic.generator import POSITION_HARD_LIMIT, POSITION_SOFT_LIMIT

    if not available_phrases:
        raise ValueError("No phrases available for selection")

    # At hard limits, force direction
    if position > POSITION_HARD_LIMIT:
        # Too far forward, must go backward or stay neutral
        valid = [p for p in available_phrases if p.net_movement <= 0]
        if valid:
            return random.choice(valid)
        # Fallback if no backward phrases available
        return random.choice(available_phrases)

    if position < -POSITION_HARD_LIMIT:
        # Too far backward, must go forward or stay neutral
        valid = [p for p in available_phrases if p.net_movement >= 0]
        if valid:
            return random.choice(valid)
        # Fallback if no forward phrases available
        return random.choice(available_phrases)

    # Within limits, use weighted selection
    weights = []
    for phrase in available_phrases:
        # Start with phrase's base weight (e.g., 0.5 for attack phrases)
        weight = phrase.weight

        # Beyond soft limit, bias toward return direction
        if position > POSITION_SOFT_LIMIT:
            # Far forward, prefer backward movement
            if phrase.net_movement < 0:
                weight *= 2.0  # Prefer backward
            elif phrase.net_movement > 0:
                weight *= 0.5  # Discourage forward
        elif position < -POSITION_SOFT_LIMIT:
            # Far backward, prefer forward movement
            if phrase.net_movement > 0:
                weight *= 2.0  # Prefer forward
            elif phrase.net_movement < 0:
                weight *= 0.5  # Discourage backward

        weights.append(weight)

    return random.choices(available_phrases, weights=weights, k=1)[0]
