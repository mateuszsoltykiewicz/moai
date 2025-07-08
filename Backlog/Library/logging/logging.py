import logging
import logging.config
import os

_DEFAULT_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": "app.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf8"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO"
        }
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "INFO"
    }
}

def setup_logging(config: dict = None):
    """
    Configure logging using a config dict (from config component).
    Example config keys: log_level, log_file, max_bytes, backup_count.
    """
    log_config = _DEFAULT_LOG_CONFIG.copy()
    if config:
        # Set log file path and create directory if needed
        log_file = config.get("log_file", "app.log")
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_config["handlers"]["file"]["filename"] = log_file

        # Set log level
        log_level = config.get("log_level", "INFO").upper()
        log_config["root"]["level"] = log_level
        log_config["handlers"]["console"]["level"] = log_level

        # Set rotation parameters
        log_config["handlers"]["file"]["maxBytes"] = int(config.get("max_bytes", 10 * 1024 * 1024))
        log_config["handlers"]["file"]["backupCount"] = int(config.get("backup_count", 5))

    logging.config.dictConfig(log_config)

def get_logger(name=None):
    """
    Get a logger for the given module or class.
    Usage: logger = get_logger(__name__)
    """
    return logging.getLogger(name)
