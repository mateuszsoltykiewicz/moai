# Logging Component

## Overview

Centralized, production-grade logging system for all microservices and libraries.  
**Logging configuration (level, file, rotation) is fetched from the config component and passed to `setup_logging()` at startup.**

## Features

- **Configurable Log Level**: Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Rotating File Handler**: Log files rotate automatically based on max size
- **Backup Management**: Configurable number of backup log files
- **Directory Creation**: Automatically creates log directory if missing
- **Centralized Logger**: Use `get_logger(__name__)` for module-level logging
- **Config-Driven**: All settings are fetched from the config component

## Usage Example

from Library.logging import setup_logging, get_logger
log_config = {
"log_level": "DEBUG",
"log_file": "logs/app.log",
"max_bytes": 510241024,
"backup_count": 3
}
setup_logging(log_config)
logger = get_logger(name)
logger.info("Logger initialized!")

## Configuration

| Parameter     | Description                       | Default         |
|---------------|-----------------------------------|-----------------|
| `log_level`   | Logging level                     | `'INFO'`        |
| `log_file`    | Log file path                     | `'app.log'`     |
| `max_bytes`   | Max file size before rotation     | `10*1024*1024`  |
| `backup_count`| Number of rotated backups to keep | `5`             |

## Interactions

- **Config Component**: Fetches logging config and passes it to `setup_logging()`
- **All Components**: Use `get_logger()` for consistent logging

## Security

- Log files are rotated to prevent disk exhaustion.
- Sensitive data should not be logged at any level.

## Potential Improvements

- Add JSON log formatting for structured logs
- Support for logging to syslog or remote aggregators
- Dynamic runtime log level changes

## Potential Bug Sources

- Insufficient disk space for log files
- Incorrect file permissions on log directory
- Logging misconfiguration causing silent failures

## Logging

- All logs are written with timestamp, logger name, level, and message.
- Errors and exceptions should include stack traces via `exc_info=True`.

## Last Updated

2025-06-28
