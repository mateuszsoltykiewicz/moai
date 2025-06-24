class AppLibException(Exception):
    """Base exception for all AppLib errors."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.details = details or {}
