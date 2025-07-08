# /Python/libraries/core/async_logging/__init__.py
import logging
import json
from logging.handlers import RotatingFileHandler

def setup_async_logger(name, logfile="service.log", max_bytes=10*1024*1024, backup_count=5):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(logfile, maxBytes=max_bytes, backupCount=backup_count)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    return logger

def json_log(record, uuid, correlation_id):
    return json.dumps({
        "message": record.getMessage(),
        "level": record.levelname,
        "uuid": uuid,
        "correlation_id": correlation_id
    })
