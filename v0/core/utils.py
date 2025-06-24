"""
Core utility functions for AppLib.

These helpers are used by multiple core models, services, or validators.
"""

from datetime import datetime, timezone

def utcnow_isoformat() -> str:
    """
    Returns the current UTC time in ISO 8601 format.
    Used for timestamps in domain events and models.
    """
    return datetime.now(timezone.utc).isoformat()

def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Restricts a value to a given range.
    Used in business logic (e.g., rate limiting, score normalization).
    """
    return max(min_value, min(value, max_value))

def generate_device_id(prefix: str = "dev") -> str:
    """
    Generates a unique device ID with a given prefix.
    """
    from uuid import uuid4
    return f"{prefix}_{uuid4().hex[:8]}"

# Add more utilities as your core logic evolves
