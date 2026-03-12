"""Shared test utilities for config.settings unit tests."""

from pathlib import Path

from config.helper import PROJECT_ROOT

APP_ENVS = ("dev", "staging", "production")


def expected_config_path(environment: str) -> Path:
    """Return expected config directory path for an environment."""
    return PROJECT_ROOT / "config" / environment


def expected_test_data_root() -> Path:
    """Return the root path for golden/case test data."""
    return PROJECT_ROOT / "test_data"


def expected_module_data_root(module_name: str) -> Path:
    """Return the test_data root for a test module path suffix."""
    return expected_test_data_root() / "unit/config/settings" / module_name
