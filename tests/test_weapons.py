"""Tests for logic/weapons.py - Weapon profiles and configurations."""
import pytest


class TestWeaponType:
    """Test WeaponType enum."""

    def test_weapon_type_has_foil(self):
        """WeaponType should have FOIL with value 'foil'."""
        from logic.weapons import WeaponType

        assert WeaponType.FOIL.value == "foil"

    def test_weapon_type_has_epee(self):
        """WeaponType should have EPEE with value 'epee'."""
        from logic.weapons import WeaponType

        assert WeaponType.EPEE.value == "epee"

    def test_weapon_type_has_sabre(self):
        """WeaponType should have SABRE with value 'sabre'."""
        from logic.weapons import WeaponType

        assert WeaponType.SABRE.value == "sabre"


class TestWeaponProfile:
    """Test WeaponProfile dataclass."""

    def test_weapon_profile_has_required_fields(self):
        """WeaponProfile should have weapon_type, tempo_multiplier, command_weights, additional_commands."""
        from logic.weapons import WeaponProfile, WeaponType

        profile = WeaponProfile(
            weapon_type=WeaponType.FOIL,
            tempo_multiplier=1.0,
            command_weights={"balancez": 0.3},
            additional_commands=[],
        )

        assert profile.weapon_type == WeaponType.FOIL
        assert profile.tempo_multiplier == 1.0
        assert profile.command_weights == {"balancez": 0.3}
        assert profile.additional_commands == []


class TestWeaponProfiles:
    """Test WEAPON_PROFILES dictionary."""

    def test_foil_tempo_multiplier(self):
        """Foil should have tempo_multiplier of 1.0 (standard)."""
        from logic.weapons import WEAPON_PROFILES

        profile = WEAPON_PROFILES["foil"]
        assert profile.tempo_multiplier == 1.0

    def test_epee_tempo_multiplier(self):
        """Epee should have tempo_multiplier of 0.8 (slower)."""
        from logic.weapons import WEAPON_PROFILES

        profile = WEAPON_PROFILES["epee"]
        assert profile.tempo_multiplier == 0.8

    def test_sabre_tempo_multiplier(self):
        """Sabre should have tempo_multiplier of 1.3 (faster)."""
        from logic.weapons import WEAPON_PROFILES

        profile = WEAPON_PROFILES["sabre"]
        assert profile.tempo_multiplier == 1.3

    def test_foil_balancez_weight(self):
        """Foil should have balancez weight of 0.3 (less common)."""
        from logic.weapons import WEAPON_PROFILES

        profile = WEAPON_PROFILES["foil"]
        assert profile.command_weights.get("balancez") == 0.3

    def test_epee_balancez_weight(self):
        """Epee should have balancez weight of 1.5 (more common)."""
        from logic.weapons import WEAPON_PROFILES

        profile = WEAPON_PROFILES["epee"]
        assert profile.command_weights.get("balancez") == 1.5

    def test_sabre_balancez_weight(self):
        """Sabre should have balancez weight of 0.0 (excluded)."""
        from logic.weapons import WEAPON_PROFILES

        profile = WEAPON_PROFILES["sabre"]
        assert profile.command_weights.get("balancez") == 0.0

    def test_foil_no_additional_commands(self):
        """Foil should have no additional commands."""
        from logic.weapons import WEAPON_PROFILES

        profile = WEAPON_PROFILES["foil"]
        assert profile.additional_commands == []

    def test_epee_no_additional_commands(self):
        """Epee should have no additional commands."""
        from logic.weapons import WEAPON_PROFILES

        profile = WEAPON_PROFILES["epee"]
        assert profile.additional_commands == []

    def test_sabre_includes_fleche(self):
        """Sabre should include fleche in additional_commands."""
        from logic.weapons import WEAPON_PROFILES

        profile = WEAPON_PROFILES["sabre"]
        assert "fleche" in profile.additional_commands


class TestGetWeaponProfile:
    """Test get_weapon_profile helper function."""

    def test_get_foil_profile(self):
        """get_weapon_profile('foil') should return foil profile."""
        from logic.weapons import get_weapon_profile, WeaponType

        profile = get_weapon_profile("foil")
        assert profile.weapon_type == WeaponType.FOIL
        assert profile.tempo_multiplier == 1.0

    def test_get_epee_profile(self):
        """get_weapon_profile('epee') should return epee profile."""
        from logic.weapons import get_weapon_profile, WeaponType

        profile = get_weapon_profile("epee")
        assert profile.weapon_type == WeaponType.EPEE
        assert profile.tempo_multiplier == 0.8

    def test_get_sabre_profile(self):
        """get_weapon_profile('sabre') should return sabre profile."""
        from logic.weapons import get_weapon_profile, WeaponType

        profile = get_weapon_profile("sabre")
        assert profile.weapon_type == WeaponType.SABRE
        assert profile.tempo_multiplier == 1.3

    def test_get_invalid_weapon_raises_keyerror(self):
        """get_weapon_profile('invalid') should raise KeyError."""
        from logic.weapons import get_weapon_profile

        with pytest.raises(KeyError):
            get_weapon_profile("invalid")
