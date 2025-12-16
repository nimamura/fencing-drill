"""E2E tests for session completion behavior."""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestSessionCompletion:
    """Test UI state after session completes naturally."""

    def test_start_button_visible_after_session_completes(
        self, page: Page, server: str
    ):
        """After a session completes naturally, the start button should be visible.

        This tests the bug where the start button disappears after a training
        session completes without user intervention (i.e., all commands are
        executed and the session ends on its own).
        """
        page.goto(server)

        # Basic mode is selected by default
        # Set minimum repetitions (5) for quick test
        page.fill('input[name="repetitions"]', "5")
        # Set fastest tempo (120 BPM = 0.5s interval)
        page.fill('input[name="tempo_bpm"]', "120")

        # Click start button
        page.click("#btn-start")

        # Wait for session to complete and start button to reappear
        # With 5 reps at 120 BPM, session should complete in about 3-4 seconds
        start_button = page.locator("#btn-start")
        start_button.wait_for(state="visible", timeout=30000)

        # Verify start button is visible
        expect(start_button).to_be_visible()

        # Verify stop button is not visible
        stop_button = page.locator("#btn-stop")
        expect(stop_button).not_to_be_visible()

    def test_can_start_new_session_after_completion(self, page: Page, server: str):
        """After a session completes, user should be able to start a new session.

        This ensures the app returns to a fully functional initial state.
        """
        page.goto(server)

        # First session - minimum repetitions
        page.fill('input[name="repetitions"]', "5")
        page.fill('input[name="tempo_bpm"]', "120")
        page.click("#btn-start")

        # Wait for session to complete
        start_button = page.locator("#btn-start")
        start_button.wait_for(state="visible", timeout=30000)

        # Start second session - this should work if UI is properly restored
        page.click("#btn-start")

        # Verify stop button appears (session started)
        stop_button = page.locator("#btn-stop")
        stop_button.wait_for(state="visible", timeout=10000)
        expect(stop_button).to_be_visible()

        # Clean up - stop the session
        page.click("#btn-stop")
