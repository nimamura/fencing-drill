"""Tests for phrase-based command generation."""
import pytest
import random


class TestPhraseDefinition:
    """Test Phrase dataclass and PHRASES constant."""

    def test_phrase_has_required_fields(self):
        """Phrase should have id, name, commands, net_movement, and difficulty."""
        from logic.phrases import Phrase

        phrase = Phrase(
            id="test",
            name="Test Phrase",
            commands=["marche", "rompe"],
            net_movement=0.0,
            difficulty="beginner",
        )

        assert phrase.id == "test"
        assert phrase.name == "Test Phrase"
        assert phrase.commands == ["marche", "rompe"]
        assert phrase.net_movement == 0.0
        assert phrase.difficulty == "beginner"

    def test_phrases_constant_exists(self):
        """PHRASES constant should be defined."""
        from logic.phrases import PHRASES

        assert isinstance(PHRASES, dict)
        assert len(PHRASES) > 0

    def test_phrase_net_movement_matches_sum(self):
        """Each phrase's net_movement should match sum of command position effects."""
        from logic.phrases import PHRASES
        from logic.commands import POSITION_EFFECTS

        for phrase_id, phrase in PHRASES.items():
            expected_sum = sum(POSITION_EFFECTS.get(cmd, 0.0) for cmd in phrase.commands)
            assert phrase.net_movement == expected_sum, (
                f"Phrase {phrase_id}: net_movement {phrase.net_movement} "
                f"doesn't match sum {expected_sum}"
            )

    def test_all_commands_in_phrases_are_valid(self):
        """All command IDs in phrases should exist in COMMANDS."""
        from logic.phrases import PHRASES
        from logic.commands import COMMANDS

        for phrase_id, phrase in PHRASES.items():
            for cmd in phrase.commands:
                assert cmd in COMMANDS, f"Invalid command '{cmd}' in phrase '{phrase_id}'"


class TestPhrasesByDifficulty:
    """Test filtering phrases by difficulty level."""

    def test_get_phrases_for_beginner(self):
        """Beginner phrases should only include basic commands."""
        from logic.phrases import get_phrases_for_difficulty

        phrases = get_phrases_for_difficulty("beginner")

        assert len(phrases) > 0
        for phrase in phrases:
            assert phrase.difficulty == "beginner"

    def test_get_phrases_for_intermediate(self):
        """Intermediate phrases should include beginner and intermediate."""
        from logic.phrases import get_phrases_for_difficulty

        phrases = get_phrases_for_difficulty("intermediate")

        assert len(phrases) > 0
        difficulties = {p.difficulty for p in phrases}
        assert "intermediate" in difficulties or "beginner" in difficulties

    def test_get_phrases_for_advanced(self):
        """Advanced should include all difficulty levels."""
        from logic.phrases import get_phrases_for_difficulty

        phrases = get_phrases_for_difficulty("advanced")

        # Advanced should have the most phrases
        beginner = get_phrases_for_difficulty("beginner")
        assert len(phrases) >= len(beginner)

    def test_invalid_difficulty_returns_beginner(self):
        """Invalid difficulty should fall back to beginner."""
        from logic.phrases import get_phrases_for_difficulty

        phrases = get_phrases_for_difficulty("invalid")
        beginner = get_phrases_for_difficulty("beginner")

        assert phrases == beginner


class TestPhraseSelection:
    """Test position-aware phrase selection."""

    def test_select_balanced_phrase_returns_phrase(self):
        """select_balanced_phrase should return a Phrase object."""
        from logic.phrases import select_balanced_phrase, get_phrases_for_difficulty

        phrases = get_phrases_for_difficulty("intermediate")
        phrase = select_balanced_phrase(0.0, phrases)

        assert phrase is not None
        assert phrase in phrases

    def test_select_balanced_phrase_neutral_position(self):
        """At neutral position, should select from all phrases."""
        from logic.phrases import select_balanced_phrase, get_phrases_for_difficulty

        random.seed(42)

        phrases = get_phrases_for_difficulty("intermediate")
        selected_ids = set()

        # Run many iterations to see variety
        for _ in range(100):
            phrase = select_balanced_phrase(0.0, phrases)
            selected_ids.add(phrase.id)

        # Should select variety of phrases (not just one type)
        assert len(selected_ids) > 1

    def test_select_balanced_phrase_forward_bias(self):
        """When far backward, should prefer forward-moving phrases."""
        from logic.phrases import select_balanced_phrase, get_phrases_for_difficulty

        random.seed(42)

        phrases = get_phrases_for_difficulty("intermediate")
        # Position far backward (-4.0)
        position = -4.0

        forward_count = 0
        backward_count = 0

        for _ in range(100):
            phrase = select_balanced_phrase(position, phrases)
            if phrase.net_movement > 0:
                forward_count += 1
            elif phrase.net_movement < 0:
                backward_count += 1

        # Should prefer forward movement
        assert forward_count > backward_count, (
            f"Expected forward > backward, got {forward_count} vs {backward_count}"
        )

    def test_select_balanced_phrase_backward_bias(self):
        """When far forward, should prefer backward-moving phrases."""
        from logic.phrases import select_balanced_phrase, get_phrases_for_difficulty

        random.seed(42)

        phrases = get_phrases_for_difficulty("intermediate")
        # Position far forward (+4.0)
        position = 4.0

        forward_count = 0
        backward_count = 0

        for _ in range(100):
            phrase = select_balanced_phrase(position, phrases)
            if phrase.net_movement > 0:
                forward_count += 1
            elif phrase.net_movement < 0:
                backward_count += 1

        # Should prefer backward movement
        assert backward_count > forward_count, (
            f"Expected backward > forward, got {backward_count} vs {forward_count}"
        )

    def test_hard_limit_forces_backward_phrases(self):
        """Beyond hard limit forward, must select backward phrases."""
        from logic.phrases import select_balanced_phrase, get_phrases_for_difficulty
        from logic.generator import POSITION_HARD_LIMIT

        random.seed(42)

        phrases = get_phrases_for_difficulty("intermediate")
        # Position beyond hard limit
        position = POSITION_HARD_LIMIT + 1.0

        for _ in range(20):
            phrase = select_balanced_phrase(position, phrases)
            # Should only select neutral or backward movement
            assert phrase.net_movement <= 0, (
                f"At position {position}, selected forward phrase: {phrase.id}"
            )

    def test_hard_limit_forces_forward_phrases(self):
        """Beyond hard limit backward, must select forward phrases."""
        from logic.phrases import select_balanced_phrase, get_phrases_for_difficulty
        from logic.generator import POSITION_HARD_LIMIT

        random.seed(42)

        phrases = get_phrases_for_difficulty("intermediate")
        # Position beyond negative hard limit
        position = -POSITION_HARD_LIMIT - 1.0

        for _ in range(20):
            phrase = select_balanced_phrase(position, phrases)
            # Should only select neutral or forward movement
            assert phrase.net_movement >= 0, (
                f"At position {position}, selected backward phrase: {phrase.id}"
            )

    def test_select_balanced_phrase_empty_list_raises(self):
        """Empty phrase list should raise ValueError."""
        from logic.phrases import select_balanced_phrase

        with pytest.raises(ValueError):
            select_balanced_phrase(0.0, [])


class TestPhraseContent:
    """Test specific phrase content requirements."""

    def test_footwork_drill_exists(self):
        """Footwork drill phrase should exist (marche/rompe alternation)."""
        from logic.phrases import PHRASES

        footwork_phrases = [
            p for p in PHRASES.values()
            if "marche" in p.commands and "rompe" in p.commands
        ]
        assert len(footwork_phrases) > 0

    def test_attack_phrase_exists(self):
        """Attack phrase should exist (includes fendez + remise)."""
        from logic.phrases import PHRASES

        attack_phrases = [
            p for p in PHRASES.values()
            if "fendez" in p.commands and "remise" in p.commands
        ]
        assert len(attack_phrases) > 0

    def test_prep_attack_phrase_exists(self):
        """Prep attack phrase should exist (allongez + fendez)."""
        from logic.phrases import PHRASES

        prep_phrases = [
            p for p in PHRASES.values()
            if "allongez" in p.commands and "fendez" in p.commands
        ]
        assert len(prep_phrases) > 0

    def test_bond_phrase_exists_in_advanced(self):
        """Bond drill phrase should exist in advanced difficulty."""
        from logic.phrases import PHRASES

        bond_phrases = [
            p for p in PHRASES.values()
            if "bond_avant" in p.commands or "bond_arriere" in p.commands
        ]
        assert len(bond_phrases) > 0

        # Bond phrases should be advanced
        for phrase in bond_phrases:
            assert phrase.difficulty == "advanced"
