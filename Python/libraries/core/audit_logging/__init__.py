# /Python/libraries/core/audit_logging/__init__.py
import logging
import json

def audit_log(action, uuid, user=None, details=None):
    record = {
        "action": action,
        "uuid": uuid,
        "user": user,
        "details": details
    }
    logging.info(json.dumps(record))
