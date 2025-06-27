"""
Logging utilities with severity levels.
"""

import logging

def log_info(message: str):
    logging.info(f"[mTLS] {message}")

def log_error(message: str):
    logging.error(f"[mTLS] ERROR: {message}")

def log_debug(message: str):
    logging.debug(f"[mTLS] {message}")
