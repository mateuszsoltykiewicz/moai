from .base import AppLibException

class mTLSException(AppLibException):
    """General mTLS/certificate error."""

class CertificateExpiredError(mTLSException):
    """Certificate has expired."""

class CertificateValidationError(mTLSException):
    """Certificate validation failed."""
