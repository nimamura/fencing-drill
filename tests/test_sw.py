"""Tests for Service Worker configuration."""

import re
from pathlib import Path


def test_sw_cache_version_updated_for_halte():
    """Service worker cache version should be v2 to invalidate halte translation cache."""
    sw_path = Path(__file__).parent.parent / "static" / "sw.js"
    content = sw_path.read_text()

    # Extract CACHE_NAME value
    match = re.search(r"const CACHE_NAME = ['\"]([^'\"]+)['\"]", content)
    assert match is not None, "CACHE_NAME not found in sw.js"

    cache_name = match.group(1)
    assert cache_name == "fencing-drill-v2", (
        f"CACHE_NAME should be 'fencing-drill-v2' to invalidate old cache with halte translations, "
        f"but got '{cache_name}'"
    )
