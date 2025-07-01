class HeatingJobError(Exception):
    pass

class FatalAlarmError(HeatingJobError):
    pass
