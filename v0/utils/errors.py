"""
Standardized error handling and reporting utilities.

- Consistent error response formatting for APIs.
- Custom exception classes for common domains.
- Optional integration with external error reporting (e.g., Sentry).
"""

import logging
from typing import Optional, Dict

class AppError(Exception):
    """Base class for application-specific errors."""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}

def format_error_response(exc: Exception, status_code: int = 500) -> Dict:
    """
    Format an error response for APIs.
    """
    return {
        "error": {
            "type": exc.__class__.__name__,
            "message": str(exc),
            "code": getattr(exc, "code", None),
            "details": getattr(exc, "details", None)
        },
        "status_code": status_code
    }

def log_and_report_error(exc: Exception, logger: logging.Logger):
    """
    Log the error and optionally report to external systems.
    """
    logger.error("Exception: %s", exc, exc_info=True)
    # Uncomment and configure for Sentry or other reporting
    # import sentry_sdk
    # sentry_sdk.capture_exception(exc)
