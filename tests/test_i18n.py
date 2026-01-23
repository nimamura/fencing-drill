"""Tests for internationalization (i18n) functionality."""
import os
import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


class TestI18nTranslations:
    """Tests for i18n translation data."""

    def test_i18n_js_file_exists(self):
        """i18n.js file should exist in static/js directory."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        assert os.path.exists(i18n_path), "static/js/i18n.js should exist"

    def test_i18n_js_contains_translations(self):
        """i18n.js should contain TRANSLATIONS object with ja, en, fr keys."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for TRANSLATIONS object
        assert "TRANSLATIONS" in content, "TRANSLATIONS object should be defined"
        # Check for all three languages
        assert '"ja"' in content or "'ja'" in content, "Japanese translations should exist"
        assert '"en"' in content or "'en'" in content, "English translations should exist"
        assert '"fr"' in content or "'fr'" in content, "French translations should exist"

    def test_i18n_js_has_required_keys(self):
        """i18n.js should contain all required translation keys."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_keys = [
            "header.ready",
            "mode.basic",
            "mode.combination",
            "mode.random",
            "mode.interval",
            "button.start",
            "button.stop",
            "status.idle",
        ]
        for key in required_keys:
            assert key in content, f"Translation key '{key}' should be defined"


class TestLanguageSelector:
    """Tests for language selector UI component."""

    def test_index_has_language_selector(self):
        """Main page should contain a language selector."""
        response = client.get("/")
        assert response.status_code == 200
        content = response.text

        # Check for language selector element
        assert 'id="language-selector"' in content, "Language selector should exist"

    def test_language_selector_has_all_options(self):
        """Language selector should have ja, en, fr options."""
        response = client.get("/")
        content = response.text

        assert 'value="ja"' in content, "Japanese option should exist"
        assert 'value="en"' in content, "English option should exist"
        assert 'value="fr"' in content, "French option should exist"


class TestDataI18nAttributes:
    """Tests for data-i18n attributes in HTML templates."""

    def test_index_has_data_i18n_attributes(self):
        """Main page should have data-i18n attributes for translatable text."""
        response = client.get("/")
        content = response.text

        # Check that data-i18n attributes exist
        assert "data-i18n=" in content, "data-i18n attributes should exist"

    def test_mode_labels_have_data_i18n(self):
        """Mode labels should have data-i18n attributes."""
        response = client.get("/")
        content = response.text

        # Check for mode label translations
        assert 'data-i18n="mode.basic"' in content, "Basic mode should have data-i18n"
        assert 'data-i18n="mode.combination"' in content, "Combination mode should have data-i18n"
        assert 'data-i18n="mode.random"' in content, "Random mode should have data-i18n"
        assert 'data-i18n="mode.interval"' in content, "Interval mode should have data-i18n"

    def test_buttons_have_data_i18n(self):
        """Button labels should have data-i18n attributes."""
        response = client.get("/")
        content = response.text

        assert 'data-i18n="button.start"' in content, "Start button should have data-i18n"
        assert 'data-i18n="button.stop"' in content, "Stop button should have data-i18n"

    def test_settings_basic_has_data_i18n(self):
        """Basic settings panel should have data-i18n attributes."""
        response = client.get("/settings/basic")
        content = response.text

        assert "data-i18n=" in content, "Settings basic should have data-i18n attributes"

    def test_settings_random_has_data_i18n(self):
        """Random settings panel should have data-i18n attributes."""
        response = client.get("/settings/random")
        content = response.text

        assert "data-i18n=" in content, "Settings random should have data-i18n attributes"


class TestI18nJavaScriptFunctions:
    """Tests for i18n JavaScript functions."""

    def test_i18n_js_has_apply_translations_function(self):
        """i18n.js should have applyTranslations function."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "applyTranslations" in content, "applyTranslations function should exist"

    def test_i18n_js_has_get_current_lang_function(self):
        """i18n.js should have getCurrentLang function."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "getCurrentLang" in content, "getCurrentLang function should exist"

    def test_index_includes_i18n_js(self):
        """Main page should include i18n.js script."""
        response = client.get("/")
        content = response.text

        assert "/static/js/i18n.js" in content, "i18n.js should be included in index.html"

    def test_i18n_js_has_detect_browser_lang_function(self):
        """i18n.js should have detectBrowserLang function."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "detectBrowserLang" in content, "detectBrowserLang function should exist"

    def test_i18n_js_uses_navigator_language(self):
        """i18n.js should use navigator.language for browser detection."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "navigator.language" in content, "Should use navigator.language for detection"


class TestCommandTranslations:
    """Tests for command name translations."""

    def test_i18n_js_has_command_translations(self):
        """i18n.js should have translations for command names."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Commands should have translations in all languages
        command_keys = [
            "command.marche",
            "command.rompe",
            "command.fendez",
        ]
        for key in command_keys:
            assert key in content, f"Command translation key '{key}' should be defined"

    def test_balancez_translation_exists(self):
        """command.balancez should be defined in all languages."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert '"command.balancez"' in content, "command.balancez should be defined"

    def test_balancez_japanese_description_is_correct(self):
        """Balancez Japanese description should be '揺れ動作'."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "揺れ動作" in content, "Balancez Japanese description should be '揺れ動作'"

    def test_all_commands_have_desc_translations(self):
        """All commands should have .desc translation keys."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        command_ids = [
            "en_garde", "marche", "rompe", "fendez", "allongez",
            "remise", "bond_avant", "bond_arriere", "balancez", "double_marche", "fleche"
        ]
        for cmd_id in command_ids:
            desc_key = f'"command.{cmd_id}.desc"'
            assert desc_key in content, f"{desc_key} should be defined"

    def test_double_marche_translation_exists(self):
        """command.double_marche should be defined."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert '"command.double_marche"' in content, "command.double_marche should be defined"
        assert '"command.double_marche.desc"' in content, "command.double_marche.desc should be defined"

    def test_fleche_translation_exists(self):
        """command.fleche should be defined in all languages."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert '"command.fleche"' in content, "command.fleche should be defined"
        assert '"command.fleche.desc"' in content, "command.fleche.desc should be defined"

    def test_fleche_japanese_description_is_correct(self):
        """Fleche Japanese description should be '走り突き'."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "走り突き" in content, "Fleche Japanese description should be '走り突き'"

    def test_rest_translation_exists(self):
        """command.rest should be defined in all languages for interval mode rest phase."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert '"command.rest"' in content, "command.rest should be defined"
        assert '"command.rest.desc"' in content, "command.rest.desc should be defined"

    def test_rest_japanese_translation_is_correct(self):
        """Rest Japanese translation should be 'ルポ' with description '休憩'."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "ルポ" in content, "Rest Japanese name should be 'ルポ'"
        # Check for description in Japanese section (休憩 appears as command.rest.desc value)
        assert '"command.rest.desc": "休憩"' in content or "'command.rest.desc': '休憩'" in content, \
            "Rest Japanese description should be '休憩'"

    def test_halte_translation_exists(self):
        """command.halte should be defined in all languages for session end signal."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert '"command.halte"' in content, "command.halte should be defined"
        assert '"command.halte.desc"' in content, "command.halte.desc should be defined"

    def test_halte_japanese_translation_is_correct(self):
        """Halte Japanese translation should be 'アルト' with description '止め'."""
        i18n_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "static", "js", "i18n.js"
        )
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "アルト" in content, "Halte Japanese name should be 'アルト'"
        assert '"command.halte.desc": "止め"' in content or "'command.halte.desc': '止め'" in content, \
            "Halte Japanese description should be '止め'"
