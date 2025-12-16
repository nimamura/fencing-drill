"""E2E test fixtures for Playwright."""
import pytest
import subprocess
import time
import socket


def get_free_port():
    """Get an available port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server():
    """Start a test server for E2E tests."""
    port = get_free_port()
    proc = subprocess.Popen(
        ["uvicorn", "main:app", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Wait for server to start
    time.sleep(2)

    yield f"http://localhost:{port}"

    proc.terminate()
    proc.wait(timeout=5)
