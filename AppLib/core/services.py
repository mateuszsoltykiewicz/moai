"""
Business services and use cases for AppLib Core.
"""

from core.models import Device, User
from exceptions.core import (
    DeviceAlreadyActiveError,
    DeviceAlreadyInactiveError,
    InvalidDeviceStatusError,
    UserInactiveError,
)

def activate_device(device: Device):
    """
    Activates a device if it is not already active.
    Raises DeviceAlreadyActiveError if the device is already active.
    """
    if device.status == "active":
        raise DeviceAlreadyActiveError(f"Device {device.device_id} is already active.")
    device.activate()

def deactivate_device(device: Device):
    """
    Deactivates a device if it is not already inactive.
    Raises DeviceAlreadyInactiveError if the device is already inactive.
    """
    if device.status == "inactive":
        raise DeviceAlreadyInactiveError(f"Device {device.device_id} is already inactive.")
    device.deactivate()

def validate_device_status(device: Device):
    """
    Ensures device status is one of the allowed values.
    Raises InvalidDeviceStatusError otherwise.
    """
    if device.status not in {"active", "inactive", "error"}:
        raise InvalidDeviceStatusError(f"Invalid status: {device.status}")

def ensure_user_is_active(user: User):
    """
    Ensures a user is active before performing an operation.
    Raises UserInactiveError if not.
    """
    if not user.is_active:
        raise UserInactiveError(f"User {user.user_id} is inactive.")
