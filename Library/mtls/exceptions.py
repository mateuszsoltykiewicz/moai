"""
Granular exceptions for mTLS errors.
"""

class MtlsConfigError(Exception):
    """Base configuration error"""

class MtlsCertValidationError(MtlsConfigError):
    """Certificate validation failed"""

class MtlsReloadError(MtlsConfigError):
    """Certificate reload failed"""

class MtlsEnforcementError(MtlsConfigError):
    """Enforcement mode change failed"""
