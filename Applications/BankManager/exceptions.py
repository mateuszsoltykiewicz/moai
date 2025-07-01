class BankManagerError(Exception):
    pass

class TransactionError(BankManagerError):
    pass

class FatalAlarmError(BankManagerError):
    """Triggers service crash"""
    pass
