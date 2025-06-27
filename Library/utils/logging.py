"""
Logging utilities for UtilsManager.

- Production-ready logging setup for FastAPI and all components
- Supports console, file, and JSON logging
- Works with Uvicorn and all environments
- Integrates with log rotation and centralized logging
"""

import logging
from logging.config import dictConfig
import os
from logging.handlers import RotatingFileHandler

def setup_logging(config: dict = None):
    """
    Set up logging for the application.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "app.log",
                "formatter": "json",
                "level": log_level,
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "app": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
        },
        "root": {"handlers": ["console"], "level": log_level},
    }
    dictConfig(log_config)
    logger = logging.getLogger("app")
    logger.debug("Logging system initialized")
    return logger
