"""
Logging utilities for UtilsManager.

- Provides robust, production-ready logging setup for FastAPI and all components
- Supports console, file, and JSON logging
- Works with Uvicorn and in all environments
"""

import logging
from logging.config import dictConfig
import sys
import os

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
                "class": "logging.FileHandler",
                "filename": "app.log",
                "formatter": "json",
                "level": log_level,
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
