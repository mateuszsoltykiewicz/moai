# Models

This directory contains all shared data models and schemas for the platform.

## alarms.py

- Defines the `Alarm` model and `AlarmLevel` enum for system-wide alerting.
- Used by the alarms service, metrics, and any component that needs to emit or process alarms.

## schemas.py

- Contains shared Pydantic schemas for API validation, message passing, etc.
- Extend as new features and services are added.

## Usage Example

from models.alarms import Alarm, AlarmLevel
alarm = Alarm(
  code=“DATABASE_CONNECTION_LOST”,
  message=“Database connection lost.”,
  level=AlarmLevel.CRITICAL
)