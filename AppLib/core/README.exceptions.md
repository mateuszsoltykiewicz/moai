# Exception Handling

## Overview

All exceptions in the application should inherit from `core.exceptions.CoreException`.
This ensures consistent error handling, logging, and integration with alarms/metrics systems.

## Usage

- Raise `CoreException` or its subclasses for all errors.
- Extend for subservice-specific errors as needed.
- Use the `code` and `details` fields for structured error reporting.

## Example

from core.exceptions import ValidationException
def validate_input(data):
if not data:
  raise ValidationException(“Input data missing”, code=400)