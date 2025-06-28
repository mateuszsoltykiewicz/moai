class CentralExceptionsError(Exception):
    """Base exception for CentralExceptions component"""
    pass

class ExceptionNotFoundError(CentralExceptionsError):
    """Raised when an exception record is not found"""
    pass

class ExceptionProcessingError(CentralExceptionsError):
    """Raised when processing an exception fails"""
    pass
