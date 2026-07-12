"""Shared pytest configuration for tests."""

pytest_plugins = []


def pytest_configure(config):
    """Register custom markers to suppress warnings."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (requires MinIO)"
    )
