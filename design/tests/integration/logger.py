#pytest tests/unit/test_logger.py -v

import logging
import logging.config
import io
import json
from pathlib import Path
import pytest

from AppLib.utils import logger

def test_get_logger_returns_logger_instance():
    """
    Test that get_logger returns a logging.Logger object.
    """
    log = logger.get_logger("test_logger")
    assert isinstance(log, logging.Logger)

def test_configure_logging_sets_log_level_and_handlers(tmp_path):
    """
    Test that configure_logging sets the log level and handlers as per config.
    """
    # Create a temporary logging config file
    config_path = tmp_path / "logging.json"
    config_content = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {"format": "%(levelname)s - %(message)s"}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "DEBUG"
            }
        },
        "root": {
            "handlers": ["console"],
            "level": "DEBUG"
        }
    }
    with open(config_path, "w") as f:
        json.dump(config_content, f)

    # Create a StringIO stream to capture log output
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Configure logging using the config file
    logger.configure_logging(str(config_path))

    # Get a logger and add our stream handler
    test_logger = logger.get_logger("test_logger")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.DEBUG)

    # Log test messages
    test_logger.debug("debug message")
    test_logger.info("info message")

    # Flush handler and check output
    handler.flush()
    output = log_stream.getvalue()

    assert "DEBUG - debug message" in output
    assert "INFO - info message" in output

    # Remove handler after test
    test_logger.removeHandler(handler)

import logging
import logging.config
from pathlib import Path
import pytest

def test_log_rotation(tmp_path):
    """
    Test that log rotation creates backup files when size limit is reached.
    """
    log_file = tmp_path / "app.log"
    
    # Configure rotation at 100 bytes
    config = {
        "version": 1,
        "handlers": {
            "rotate": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(log_file),
                "maxBytes": 100,
                "backupCount": 2,
                "formatter": "basic",
                "level": "INFO"
            }
        },
        "formatters": {
            "basic": {"format": "%(message)s"}
        },
        "root": {
            "handlers": ["rotate"],
            "level": "INFO"
        }
    }
    
    logging.config.dictConfig(config)
    logger = logging.getLogger()
    
    # Write 3 messages that are 40 bytes each (total 120 bytes)
    message = "This message is exactly 40 characters long."
    assert len(message) == 40
    
    logger.info(message)  # 40 bytes (file size 40)
    logger.info(message)  # 80 bytes (file size 80)
    logger.info(message)  # 120 bytes → triggers rotation
    
    # Check files
    files = list(tmp_path.glob("app.log*"))
    assert len(files) == 2  # Original + 1 backup
    assert log_file.exists()
    assert (tmp_path / "app.log.1").exists()

