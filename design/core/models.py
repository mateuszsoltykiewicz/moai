"""
Domain Models for AppLib Core

Defines business entities and value objects.
Keep models framework-agnostic and focused on business logic only.
"""

from datetime import datetime
from typing import Optional
from ..exceptions.core import DeviceAlreadyActiveError, DeviceAlreadyInactiveError

class Device:
    """
    Represents a hardware device in the platform.
    """
    def __init__(self, device_id: str, status: str, created_at: Optional[datetime] = None):
        self.device_id = device_id
        self.status = status  # e.g., 'active', 'inactive', 'error'
        self.created_at = created_at or datetime.utcnow()

    def activate(self):
        if self.status == "active":
            raise DeviceAlreadyActiveError(f"Device {self.device_id} is already active.")
        self.status = "active"

    def deactivate(self):
        if self.status == "inactive":
            raise DeviceAlreadyInactiveError(f"Device {self.device_id} is already inactive.")
        self.status = "inactive"

    def mark_error(self, reason: str):
        self.status = "error"
        self.error_reason = reason

class User:
    """
    Represents a user in the system.
    """
    def __init__(self, user_id: str, username: str, is_active: bool = True):
        self.user_id = user_id
        self.username = username
        self.is_active = is_active

    def deactivate(self):
        self.is_active = False

    def activate(self):
        self.is_active = True