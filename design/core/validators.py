"""
Business rule validators for AppLib Core.

These functions validate business invariants and raise domain exceptions on failure.
"""

from core.models import Device, User
from exceptions.core import (
    InvalidDeviceStatusError,
    UserInactiveError,
)

def validate_device_status(device: Device):
    """
    Ensures the device status is valid.
    Raises InvalidDeviceStatusError if not.
    """
    allowed = {"active", "inactive", "error"}
    if device.status not in allowed:
        raise InvalidDeviceStatusError(
            f"Device {device.device_id} has invalid status: {device.status}"
        )

def validate_user_is_active(user: User):
    """
    Ensures the user is active.
    Raises UserInactiveError if not.
    """
    if not user.is_active:
        raise UserInactiveError(f"User {user.user_id} is not active.")

def validate_device_activation(device: Device, user: User):
    """
    Example cross-entity rule: Only active users can activate devices.
    """
    validate_user_is_active(user)
    if device.status == "active":
        raise InvalidDeviceStatusError(
            f"Device {device.device_id} is already active."
        )
