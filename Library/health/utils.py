"""
Logging utilities with severity levels.
"""

import logging

def log_info(message: str):
    logging.info(f"[Health] {message}")

def log_warning(message: str):
    logging.warning(f"[Health] WARN: {message}")

def log_error(message: str):
    logging.error(f"[Health] ERROR: {message}")
