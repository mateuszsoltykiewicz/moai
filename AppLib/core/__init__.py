"""
AppLib Core Package

This package contains all business logic, domain models, services, validators, events, and core utilities for the platform.
"""

# Expose key classes/functions for convenient import, if desired.
from .models import Device, User
from .services import activate_device, deactivate_device, validate_device_status, ensure_user_is_active
from .validators import validate_device_status, validate_user_is_active, validate_device_activation
from .events import DeviceActivated, DeviceDeactivated, UserDeactivated

# Note: You can comment out or add to the above as your public API evolves.

# If you want to keep the package "clean" and force explicit imports, you can leave __init__.py empty,
# which is also considered good practice in many modern Python projects[#1][#5].
