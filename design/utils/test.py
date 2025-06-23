"""
Developer and test helpers.

- Utilities for mocking, test data, and asserting logs/metrics.
"""

from unittest.mock import patch
from os import environ

def mock_env_vars(env_vars: dict):
    """
    Temporarily set environment variables for testing.
    """
    return patch.dict(environ, env_vars)
