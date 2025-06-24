"""
Domain (core) exceptions for business rule violations.
"""

class DeviceError(Exception):
    """Base exception for device-related errors."""
    pass

class DeviceAlreadyActiveError(DeviceError):
    """Raised when attempting to activate an already active device."""
    pass

class DeviceAlreadyInactiveError(DeviceError):
    """Raised when attempting to deactivate an already inactive device."""
    pass

class InvalidDeviceStatusError(DeviceError):
    """Raised when a device has an invalid status."""
    pass

class UserError(Exception):
    """Base exception for user-related errors."""
    pass

class UserInactiveError(UserError):
    """Raised when an operation is attempted on an inactive user."""
    pass

"""
Core exceptions for API and business logic

These exceptions are used across the application for consistent error handling.
All exceptions inherit from FastAPI's HTTPException for seamless integration
with FastAPI error handlers and OpenAPI documentation.
"""

from fastapi import HTTPException, status

class UnauthorizedError(HTTPException):
    """
    Raised when authentication is required but missing or invalid.
    """
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )

class ForbiddenError(HTTPException):
    """
    Raised when the user does not have sufficient permissions.
    """
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class NotFoundError(HTTPException):
    """
    Raised when a requested resource is not found.
    """
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class ValidationError(HTTPException):
    """
    Raised when request data fails validation.
    """
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class ServiceUnavailableError(HTTPException):
    """
    Raised when a required service or resource is unavailable.
    """
    def __init__(self, detail: str = "Service unavailable"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )
