class StateServerError(Exception):
    pass

class StateNotFoundError(StateServerError):
    pass

class StateValidationError(StateServerError):
    pass
