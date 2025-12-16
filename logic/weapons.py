"""Weapon profiles and configurations for fencing training."""
from dataclasses import dataclass, field
from enum import Enum


class WeaponType(Enum):
    """Available fencing weapons."""

    FOIL = "foil"
    EPEE = "epee"
    SABRE = "sabre"


@dataclass
class WeaponProfile:
    """Weapon-specific configuration affecting training.

    Attributes:
        weapon_type: The type of weapon.
        tempo_multiplier: Multiplier for tempo (1.0 = normal, <1 = slower, >1 = faster).
        command_weights: Dict of command_id to weight (default 1.0, 0.0 = excluded).
        additional_commands: List of weapon-specific commands to include.
    """

    weapon_type: WeaponType
    tempo_multiplier: float
    command_weights: dict[str, float] = field(default_factory=dict)
    additional_commands: list[str] = field(default_factory=list)


# Pre-defined weapon profiles
WEAPON_PROFILES: dict[str, WeaponProfile] = {
    "foil": WeaponProfile(
        weapon_type=WeaponType.FOIL,
        tempo_multiplier=1.0,
        command_weights={
            "balancez": 0.3,
            "bond_avant": 0.8,
            "bond_arriere": 0.8,
        },
        additional_commands=[],
    ),
    "epee": WeaponProfile(
        weapon_type=WeaponType.EPEE,
        tempo_multiplier=0.8,
        command_weights={
            "balancez": 1.5,
            "allongez": 1.2,
            "bond_avant": 0.5,
            "bond_arriere": 0.5,
        },
        additional_commands=[],
    ),
    "sabre": WeaponProfile(
        weapon_type=WeaponType.SABRE,
        tempo_multiplier=1.3,
        command_weights={
            "balancez": 0.0,
            "allongez": 0.8,
            "bond_avant": 1.5,
            "bond_arriere": 1.0,
        },
        additional_commands=["fleche"],
    ),
}


def get_weapon_profile(weapon: str) -> WeaponProfile:
    """Get weapon profile by weapon type string.

    Args:
        weapon: The weapon type string ('foil', 'epee', or 'sabre').

    Returns:
        The WeaponProfile for the specified weapon.

    Raises:
        KeyError: If the weapon type is not found.
    """
    return WEAPON_PROFILES[weapon]
