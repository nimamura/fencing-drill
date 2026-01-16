"""Tests for position tracking in fencing drills."""
import pytest


class TestPositionEffects:
    """Test POSITION_EFFECTS constant definition."""

    def test_position_effects_defined_for_all_commands(self):
        """POSITION_EFFECTS should have an entry for all commands in COMMANDS."""
        from logic.commands import COMMANDS, POSITION_EFFECTS

        for cmd_id in COMMANDS:
            assert cmd_id in POSITION_EFFECTS, f"Missing position effect for {cmd_id}"

    def test_forward_commands_have_positive_effect(self):
        """Forward movement commands should have positive position effect."""
        from logic.commands import POSITION_EFFECTS

        assert POSITION_EFFECTS["marche"] > 0
        assert POSITION_EFFECTS["double_marche"] > 0
        assert POSITION_EFFECTS["bond_avant"] > 0
        assert POSITION_EFFECTS["fendez"] > 0
        assert POSITION_EFFECTS["fleche"] > 0

    def test_backward_commands_have_negative_effect(self):
        """Backward movement commands should have negative position effect."""
        from logic.commands import POSITION_EFFECTS

        assert POSITION_EFFECTS["rompe"] < 0
        assert POSITION_EFFECTS["bond_arriere"] < 0
        assert POSITION_EFFECTS["remise"] < 0  # Return from lunge

    def test_neutral_commands_have_zero_effect(self):
        """Neutral commands should have zero position effect."""
        from logic.commands import POSITION_EFFECTS

        assert POSITION_EFFECTS["allongez"] == 0.0
        assert POSITION_EFFECTS["balancez"] == 0.0
        assert POSITION_EFFECTS["en_garde"] == 0.0


class TestPositionTracker:
    """Test PositionTracker class."""

    def test_tracker_initial_position_is_zero(self):
        """PositionTracker should start at position 0."""
        from logic.generator import PositionTracker

        tracker = PositionTracker()
        assert tracker.position == 0.0

    def test_tracker_accumulates_forward_movement(self):
        """Tracker should accumulate forward movement commands."""
        from logic.generator import PositionTracker

        tracker = PositionTracker()
        tracker.apply_command("marche")  # +1.0
        assert tracker.position == 1.0

        tracker.apply_command("marche")  # +1.0
        assert tracker.position == 2.0

        tracker.apply_command("double_marche")  # +2.0
        assert tracker.position == 4.0

    def test_tracker_accumulates_backward_movement(self):
        """Tracker should accumulate backward movement commands."""
        from logic.generator import PositionTracker

        tracker = PositionTracker()
        tracker.apply_command("rompe")  # -1.0
        assert tracker.position == -1.0

        tracker.apply_command("rompe")  # -1.0
        assert tracker.position == -2.0

        tracker.apply_command("bond_arriere")  # -1.5
        assert tracker.position == -3.5

    def test_tracker_handles_mixed_movement(self):
        """Tracker should handle mixed forward/backward movement."""
        from logic.generator import PositionTracker

        tracker = PositionTracker()
        tracker.apply_command("marche")  # +1.0
        tracker.apply_command("marche")  # +1.0
        tracker.apply_command("rompe")  # -1.0
        assert tracker.position == 1.0

    def test_tracker_handles_fendez_remise_cycle(self):
        """Fendez followed by remise should return to original position."""
        from logic.generator import PositionTracker

        tracker = PositionTracker()
        tracker.apply_command("marche")  # +1.0
        original_position = tracker.position

        tracker.apply_command("fendez")  # +2.0
        assert tracker.position == original_position + 2.0

        tracker.apply_command("remise")  # -2.0
        assert tracker.position == original_position

    def test_tracker_reset(self):
        """Tracker reset should return position to zero."""
        from logic.generator import PositionTracker

        tracker = PositionTracker()
        tracker.apply_command("marche")
        tracker.apply_command("marche")
        assert tracker.position != 0.0

        tracker.reset()
        assert tracker.position == 0.0

    def test_tracker_neutral_commands_dont_change_position(self):
        """Neutral commands should not change tracker position."""
        from logic.generator import PositionTracker

        tracker = PositionTracker()
        tracker.apply_command("marche")  # +1.0
        position_before = tracker.position

        tracker.apply_command("allongez")  # 0
        assert tracker.position == position_before

        tracker.apply_command("balancez")  # 0
        assert tracker.position == position_before

    def test_tracker_unknown_command_defaults_to_zero(self):
        """Unknown commands should default to zero position effect."""
        from logic.generator import PositionTracker

        tracker = PositionTracker()
        tracker.apply_command("unknown_command")
        assert tracker.position == 0.0


class TestPositionBias:
    """Test position-based direction bias."""

    def test_get_position_bias_neutral_near_origin(self):
        """Near origin (position 0), bias should be neutral."""
        from logic.generator import PositionTracker

        tracker = PositionTracker()
        assert tracker.get_position_bias() == "neutral"

        tracker.position = 2.0
        assert tracker.get_position_bias() == "neutral"

        tracker.position = -2.0
        assert tracker.get_position_bias() == "neutral"

    def test_get_position_bias_backward_when_far_forward(self):
        """When far forward (>3.0), bias should be backward."""
        from logic.generator import PositionTracker

        tracker = PositionTracker()
        tracker.position = 4.0
        assert tracker.get_position_bias() == "backward"

        tracker.position = 5.0
        assert tracker.get_position_bias() == "backward"

    def test_get_position_bias_forward_when_far_backward(self):
        """When far backward (<-3.0), bias should be forward."""
        from logic.generator import PositionTracker

        tracker = PositionTracker()
        tracker.position = -4.0
        assert tracker.get_position_bias() == "forward"

        tracker.position = -5.0
        assert tracker.get_position_bias() == "forward"
