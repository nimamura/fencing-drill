"""Pytest configuration for async tests."""
import pytest


@pytest.fixture(scope="function")
def event_loop_policy():
    """Use default event loop policy."""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="function")
def anyio_backend():
    """Use asyncio as the async backend."""
    return "asyncio"
