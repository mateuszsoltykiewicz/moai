# Logging Utility

This module provides a production-ready logging utility for all AppLib components.

## Features

- Per-module loggers
- Configurable log level, format, and handlers via JSON
- Console and file logging
- Easy integration with log aggregators (e.g., ELK, Loki)
- Structured logging for observability

## Usage

from AppLib.utils.logger import configure_logging, get_logger

Configure logging at application startup
configure_logging(“configs/dev/logging.json”)

Get a logger for your module
logger = get_logger(name)
logger.info(“Service started”) logger.error(“Something went wrong!”)

## Log Rotation

Configure log rotation in your logging config:
{
  “handlers”: {
    “file”: {
      “class”: “logging.handlers.RotatingFileHandler”,
      “filename”: “logs/app.log”,
      “maxBytes”: 1048576,  
      // Rotate after 1MB
      “backupCount”: 5       // Keep 5 backups
    }
  }
}


**Parameters:**
- `maxBytes`: Rotate when file reaches this size (bytes)
- `backupCount`: Number of backup files to retain
- `encoding`: File encoding (recommended: utf8)

**Best Practices:**
- Set `backupCount` based on disk space requirements
- Monitor log directory for excessive file growth
- Use `TimedRotatingFileHandler` for time-based rotation


## Configuration

- Place your logging config in `configs/dev/logging.json` or similar.
- Supports all standard Python logging features.
- Example config enables both console and file logging with detailed formatting.

## Best Practices

- Use per-module loggers (`get_logger(__name__)`) for clarity.
- Set log level to `DEBUG` in development, `INFO` or higher in production.
- Rotate log files in production for disk space management.
- Integrate with your cloud/logging stack as needed.

---
