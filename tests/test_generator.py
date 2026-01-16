"""Tests for logic/generator.py - Command generation per mode."""
import pytest


class TestPatterns:
    """Test combination pattern definitions."""

    def test_patterns_contains_required_patterns(self):
        """PATTERNS should contain patterns A, B, and C."""
        from logic.generator import PATTERNS

        assert "A" in PATTERNS
        assert "B" in PATTERNS
        assert "C" in PATTERNS

    def test_pattern_a_commands(self):
        """Pattern A (前進攻撃) should have correct command sequence."""
        from logic.generator import PATTERNS

        # マルシェ → マルシェ → アロンジェ・ル・ブラ → ファンドゥ → ルミーズ・アンギャルド
        expected = ["marche", "marche", "allongez", "fendez", "remise"]
        assert PATTERNS["A"] == expected

    def test_pattern_b_commands(self):
        """Pattern B (後退からの反撃) should have correct command sequence."""
        from logic.generator import PATTERNS

        # ロンペ → ロンペ → マルシェ → ファンドゥ → ルミーズ・アンギャルド
        expected = ["rompe", "rompe", "marche", "fendez", "remise"]
        assert PATTERNS["B"] == expected

    def test_pattern_c_commands(self):
        """Pattern C (フットワーク強化) should have correct command sequence."""
        from logic.generator import PATTERNS

        # マルシェ → マルシェ → ロンペ → マルシェ → ロンペ → ロンペ
        expected = ["marche", "marche", "rompe", "marche", "rompe", "rompe"]
        assert PATTERNS["C"] == expected


class TestCombinationGenerator:
    """Test combination mode command generation."""

    def test_generate_combination_returns_list(self):
        """generate_combination should return a list of command IDs."""
        from logic.generator import generate_combination
        from logic.session import CombinationConfig

        config = CombinationConfig(pattern_id="A", repetitions=1, tempo_bpm=60)
        result = generate_combination(config)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_generate_combination_pattern_a_single_rep(self):
        """generate_combination should return pattern A commands for 1 rep."""
        from logic.generator import generate_combination
        from logic.session import CombinationConfig

        config = CombinationConfig(pattern_id="A", repetitions=1, tempo_bpm=60)
        result = generate_combination(config)

        expected = ["marche", "marche", "allongez", "fendez", "remise"]
        assert result == expected

    def test_generate_combination_multiple_reps(self):
        """generate_combination should repeat pattern for multiple reps."""
        from logic.generator import generate_combination
        from logic.session import CombinationConfig

        config = CombinationConfig(pattern_id="B", repetitions=3, tempo_bpm=60)
        result = generate_combination(config)

        pattern = ["rompe", "rompe", "marche", "fendez", "remise"]
        expected = pattern * 3
        assert result == expected

    def test_generate_combination_invalid_pattern(self):
        """generate_combination should raise KeyError for invalid pattern."""
        from logic.generator import generate_combination
        from logic.session import CombinationConfig

        config = CombinationConfig(pattern_id="Z", repetitions=1, tempo_bpm=60)

        with pytest.raises(KeyError):
            generate_combination(config)


class TestIntervalGenerator:
    """Test interval mode command generation."""

    def test_generate_interval_phase_returns_work_phase(self):
        """generate_interval_work_commands should return commands for work phase."""
        from logic.generator import generate_interval_work_commands
        from logic.session import IntervalConfig

        config = IntervalConfig(work_seconds=30, rest_seconds=15, sets=5, tempo_bpm=90)
        result = generate_interval_work_commands(config)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_interval_work_commands_are_valid(self):
        """Work commands should be valid command IDs."""
        from logic.generator import generate_interval_work_commands
        from logic.session import IntervalConfig
        from logic.commands import COMMANDS

        config = IntervalConfig(work_seconds=30, rest_seconds=15, sets=5, tempo_bpm=90)
        result = generate_interval_work_commands(config)

        for cmd_id in result:
            assert cmd_id in COMMANDS, f"Invalid command: {cmd_id}"

    def test_interval_work_count_based_on_tempo(self):
        """Number of work commands should be based on tempo and duration."""
        from logic.generator import generate_interval_work_commands
        from logic.session import IntervalConfig

        # 90 BPM for 30 seconds = 30 * 90 / 60 = 45 commands
        config = IntervalConfig(work_seconds=30, rest_seconds=15, sets=5, tempo_bpm=90)
        result = generate_interval_work_commands(config)

        expected_count = int(config.work_seconds * config.tempo_bpm / 60)
        assert len(result) == expected_count


class TestRandomConstraints:
    """Test Random mode constraint logic."""

    def test_classify_command_direction(self):
        """Commands should be classified as forward, backward, or neutral."""
        from logic.generator import classify_command_direction

        # Forward commands
        assert classify_command_direction("marche") == "forward"
        assert classify_command_direction("double_marche") == "forward"
        assert classify_command_direction("bond_avant") == "forward"

        # Backward commands
        assert classify_command_direction("rompe") == "backward"
        assert classify_command_direction("bond_arriere") == "backward"

        # Neutral commands
        assert classify_command_direction("fendez") == "neutral"
        assert classify_command_direction("remise") == "neutral"
        assert classify_command_direction("balancez") == "neutral"
        assert classify_command_direction("allongez") == "neutral"

    def test_should_force_remise_after_fendez(self):
        """Fendez must be followed by remise."""
        from logic.generator import should_force_remise

        assert should_force_remise("fendez") is True
        assert should_force_remise("marche") is False
        assert should_force_remise("rompe") is False
        assert should_force_remise("remise") is False

    def test_is_bond_command(self):
        """Bond commands should be identified for longer pause."""
        from logic.generator import is_bond_command

        assert is_bond_command("bond_avant") is True
        assert is_bond_command("bond_arriere") is True
        assert is_bond_command("marche") is False
        assert is_bond_command("rompe") is False

    def test_count_consecutive_direction(self):
        """Should count consecutive commands in the same direction."""
        from logic.generator import count_consecutive_direction

        # 4 forward commands
        history = ["marche", "marche", "double_marche", "bond_avant"]
        assert count_consecutive_direction(history, "forward") == 4

        # Mixed history, last 2 are backward
        history = ["marche", "marche", "rompe", "rompe"]
        assert count_consecutive_direction(history, "backward") == 2
        assert count_consecutive_direction(history, "forward") == 0

        # Empty history
        assert count_consecutive_direction([], "forward") == 0

    def test_is_wall_risk(self):
        """Should detect wall risk when 4+ consecutive same-direction commands."""
        from logic.generator import is_wall_risk

        # 4 forward - proposing another forward is wall risk
        history = ["marche", "marche", "marche", "marche"]
        assert is_wall_risk(history, "marche") is True
        assert is_wall_risk(history, "bond_avant") is True
        assert is_wall_risk(history, "rompe") is False  # backward is ok

        # 4 backward - proposing another backward is wall risk
        history = ["rompe", "rompe", "rompe", "rompe"]
        assert is_wall_risk(history, "rompe") is True
        assert is_wall_risk(history, "marche") is False  # forward is ok

        # 3 forward - no wall risk yet
        history = ["marche", "marche", "marche"]
        assert is_wall_risk(history, "marche") is False

    def test_select_constrained_command_avoids_wall(self):
        """select_constrained_command should avoid wall risk."""
        from logic.generator import select_constrained_command
        import random

        random.seed(42)  # For reproducibility

        command_set = ["marche", "rompe"]
        history = ["marche", "marche", "marche", "marche"]

        # With 4 forward commands, should not select another forward
        for _ in range(10):
            cmd = select_constrained_command(command_set, history, None)
            assert cmd == "rompe", "Should avoid forward command to prevent wall"

    def test_select_constrained_command_forces_remise(self):
        """select_constrained_command should force remise after fendez."""
        from logic.generator import select_constrained_command

        command_set = ["marche", "rompe", "fendez", "remise"]
        history = []

        # After fendez, must select remise
        cmd = select_constrained_command(command_set, history, "fendez")
        assert cmd == "remise", "Must follow fendez with remise"

    def test_select_constrained_command_uses_command_set(self):
        """select_constrained_command should only select from command_set."""
        from logic.generator import select_constrained_command
        import random

        random.seed(42)

        command_set = ["marche", "rompe"]  # beginner set
        history = []

        for _ in range(20):
            cmd = select_constrained_command(command_set, history, None)
            assert cmd in command_set


class TestSelectConstrainedCommandWithWeapon:
    """Test select_constrained_command with weapon parameter."""

    def test_sabre_excludes_balancez(self):
        """Sabre should never select balancez (weight=0.0)."""
        from logic.generator import select_constrained_command
        import random

        random.seed(42)

        # Command set includes balancez
        command_set = ["marche", "rompe", "balancez"]
        history = []

        # Run 50 iterations - balancez should never be selected for sabre
        for _ in range(50):
            cmd = select_constrained_command(command_set, history, None, weapon="sabre")
            assert cmd != "balancez", "Sabre should not select balancez"

    def test_sabre_can_select_fleche(self):
        """Sabre should be able to select fleche (added via additional_commands)."""
        from logic.generator import select_constrained_command
        import random

        random.seed(42)

        # Command set includes fleche
        command_set = ["marche", "rompe", "fleche"]
        history = []

        # Run iterations until fleche is selected (should be possible)
        selected_fleche = False
        for _ in range(100):
            cmd = select_constrained_command(command_set, history, None, weapon="sabre")
            if cmd == "fleche":
                selected_fleche = True
                break

        assert selected_fleche, "Sabre should be able to select fleche"

    def test_foil_excludes_fleche(self):
        """Foil should never select fleche (weapon-specific to sabre)."""
        from logic.generator import select_constrained_command
        import random

        random.seed(42)

        # Command set includes fleche
        command_set = ["marche", "rompe", "fleche"]
        history = []

        # Run 50 iterations - fleche should never be selected for foil
        for _ in range(50):
            cmd = select_constrained_command(command_set, history, None, weapon="foil")
            assert cmd != "fleche", "Foil should not select fleche"

    def test_default_weapon_is_foil(self):
        """Without weapon parameter, should behave as foil (backward compatible)."""
        from logic.generator import select_constrained_command
        import random

        random.seed(42)

        command_set = ["marche", "rompe", "fleche"]
        history = []

        # Without weapon param, fleche should be excluded (foil behavior)
        for _ in range(50):
            cmd = select_constrained_command(command_set, history, None)
            assert cmd != "fleche", "Default (foil) should not select fleche"


class TestIntervalDelay:
    """Test delay calculations for interval mode."""

    def test_get_post_command_delay_normal(self):
        """Normal commands should have standard delay."""
        from logic.generator import get_post_command_delay

        base_delay = 1.0
        assert get_post_command_delay("marche", base_delay) == base_delay
        assert get_post_command_delay("rompe", base_delay) == base_delay
        assert get_post_command_delay("fendez", base_delay) == base_delay

    def test_get_post_command_delay_bond(self):
        """Bond commands should have longer delay (1.5x)."""
        from logic.generator import get_post_command_delay

        base_delay = 1.0
        expected = 1.5  # 1.5x for bond commands
        assert get_post_command_delay("bond_avant", base_delay) == expected
        assert get_post_command_delay("bond_arriere", base_delay) == expected


class TestWeaponCommandFiltering:
    """Test weapon-based command filtering."""

    def test_filter_commands_for_weapon_foil_excludes_fleche(self):
        """Foil should exclude fleche (weapon-specific command)."""
        from logic.generator import filter_commands_for_weapon
        from logic.weapons import get_weapon_profile

        command_ids = ["marche", "rompe", "fleche"]
        profile = get_weapon_profile("foil")
        result = filter_commands_for_weapon(command_ids, "foil", profile)

        assert "marche" in result
        assert "rompe" in result
        assert "fleche" not in result

    def test_filter_commands_for_weapon_sabre_includes_fleche(self):
        """Sabre should include fleche."""
        from logic.generator import filter_commands_for_weapon
        from logic.weapons import get_weapon_profile

        command_ids = ["marche", "rompe", "fleche"]
        profile = get_weapon_profile("sabre")
        result = filter_commands_for_weapon(command_ids, "sabre", profile)

        assert "marche" in result
        assert "rompe" in result
        assert "fleche" in result

    def test_filter_commands_adds_additional_commands(self):
        """Sabre should include fleche via additional_commands."""
        from logic.generator import filter_commands_for_weapon
        from logic.weapons import get_weapon_profile

        command_ids = ["marche", "rompe"]  # fleche not in list
        profile = get_weapon_profile("sabre")
        result = filter_commands_for_weapon(command_ids, "sabre", profile)

        assert "fleche" in result  # added from additional_commands


class TestWeaponWeights:
    """Test weapon-specific command weights."""

    def test_apply_weapon_weights_excludes_zero_weight(self):
        """Commands with weight 0.0 should be excluded."""
        from logic.generator import apply_weapon_weights

        command_ids = ["marche", "balancez"]
        weights = {"balancez": 0.0}  # sabre excludes balancez
        result = apply_weapon_weights(command_ids, weights)

        result_ids = [cmd_id for cmd_id, _ in result]
        assert "marche" in result_ids
        assert "balancez" not in result_ids

    def test_apply_weapon_weights_default_weight(self):
        """Commands without specific weight should default to 1.0."""
        from logic.generator import apply_weapon_weights

        command_ids = ["marche", "rompe"]
        weights = {}  # no specific weights
        result = apply_weapon_weights(command_ids, weights)

        assert result == [("marche", 1.0), ("rompe", 1.0)]

    def test_apply_weapon_weights_custom_weight(self):
        """Commands should use custom weight if specified."""
        from logic.generator import apply_weapon_weights

        command_ids = ["marche", "balancez"]
        weights = {"balancez": 0.3}  # foil reduces balancez
        result = apply_weapon_weights(command_ids, weights)

        assert ("marche", 1.0) in result
        assert ("balancez", 0.3) in result


class TestWeightedSelection:
    """Test weighted random command selection."""

    def test_select_weighted_command_returns_valid_command(self):
        """select_weighted_command should return one of the available commands."""
        from logic.generator import select_weighted_command

        weighted_commands = [("marche", 1.0), ("rompe", 1.0)]
        result = select_weighted_command(weighted_commands)

        assert result in ["marche", "rompe"]

    def test_select_weighted_command_respects_weights(self):
        """select_weighted_command should respect weights in selection."""
        import random
        from logic.generator import select_weighted_command

        random.seed(42)

        # Run many iterations with extreme weight difference
        weighted_commands = [("heavy", 100.0), ("light", 1.0)]
        results = [select_weighted_command(weighted_commands) for _ in range(100)]

        # Heavy should be selected much more often
        heavy_count = results.count("heavy")
        assert heavy_count > 80, f"Expected heavy to be selected >80 times, got {heavy_count}"

    def test_select_weighted_command_empty_raises_error(self):
        """select_weighted_command should raise ValueError for empty list."""
        from logic.generator import select_weighted_command

        with pytest.raises(ValueError):
            select_weighted_command([])

    def test_select_weighted_command_single_command(self):
        """select_weighted_command should work with single command."""
        from logic.generator import select_weighted_command

        weighted_commands = [("only_one", 1.0)]
        result = select_weighted_command(weighted_commands)

        assert result == "only_one"


class TestCommandTransitions:
    """Test command transition rules for natural movement flow."""

    def test_command_transitions_defined(self):
        """COMMAND_TRANSITIONS should be defined."""
        from logic.generator import COMMAND_TRANSITIONS

        assert isinstance(COMMAND_TRANSITIONS, dict)

    def test_allongez_has_transition_rule(self):
        """allongez should have a transition rule preferring fendez."""
        from logic.generator import COMMAND_TRANSITIONS

        assert "allongez" in COMMAND_TRANSITIONS
        rule = COMMAND_TRANSITIONS["allongez"]
        assert "next_preferred" in rule
        assert "fendez" in rule["next_preferred"]

    def test_balancez_has_transition_rule(self):
        """balancez should have a transition rule for action commands."""
        from logic.generator import COMMAND_TRANSITIONS

        assert "balancez" in COMMAND_TRANSITIONS
        rule = COMMAND_TRANSITIONS["balancez"]
        assert "next_preferred" in rule

    def test_get_preferred_next_command_after_allongez(self):
        """After allongez, should prefer fendez with ~80% probability."""
        import random
        from logic.generator import get_preferred_next_command

        random.seed(42)

        command_set = ["marche", "rompe", "fendez", "remise"]
        fendez_count = 0
        total = 1000

        for _ in range(total):
            cmd = get_preferred_next_command("allongez", command_set)
            if cmd == "fendez":
                fendez_count += 1

        # Should be around 80% fendez
        ratio = fendez_count / total
        assert 0.7 < ratio < 0.9, f"Expected ~80% fendez, got {ratio:.1%}"

    def test_get_preferred_next_command_no_rule(self):
        """Commands without transition rules should return None."""
        from logic.generator import get_preferred_next_command

        command_set = ["marche", "rompe", "fendez"]
        result = get_preferred_next_command("marche", command_set)
        assert result is None

    def test_get_preferred_next_command_preferred_not_in_set(self):
        """If preferred command not in command_set, should return None."""
        from logic.generator import get_preferred_next_command

        command_set = ["marche", "rompe"]  # No fendez
        result = get_preferred_next_command("allongez", command_set)
        # Should sometimes return None when fendez not available
        # But can also return marche (from balancez-like fallback)
        assert result is None or result in command_set

    def test_select_constrained_command_respects_transitions(self):
        """select_constrained_command should respect transition rules."""
        import random
        from logic.generator import select_constrained_command

        random.seed(42)

        command_set = ["marche", "rompe", "fendez", "remise", "allongez"]
        history = []

        # After allongez, fendez should be preferred
        fendez_count = 0
        total = 100

        for _ in range(total):
            cmd = select_constrained_command(command_set, history, "allongez")
            if cmd == "fendez":
                fendez_count += 1

        # Should see significantly more fendez than random (20% -> ~80%)
        assert fendez_count > 50, f"Expected fendez > 50%, got {fendez_count}%"
