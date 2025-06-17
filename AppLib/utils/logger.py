"""
Production-ready logging utility.

- Structured logging with per-module loggers.
- Configurable via JSON or environment variables.
- Supports console and file logging.
- Integrates with external log aggregators if needed.
"""

import logging
import logging.config
import json
import os
from pathlib import Path
from typing import Optional, Dict

DEFAULT_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        },
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO"
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO"
    }
}

def load_log_config(config_path: Optional[str] = None) -> Dict:
    """
    Load logging configuration from a JSON file, fallback to default.
    """
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return DEFAULT_LOG_CONFIG

def configure_logging(config_path: Optional[str] = None):
    """
    Configure logging and create log directories if needed.
    """
    config = load_log_config(config_path)
    
    # Auto-create directories for file handlers
    for handler in config.get("handlers", {}).values():
        if "filename" in handler:
            log_path = Path(handler["filename"])
            log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.config.dictConfig(config)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for the given module/service.
    """
    return logging.getLogger(name)
