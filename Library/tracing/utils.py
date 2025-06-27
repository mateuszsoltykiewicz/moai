import logging

def log_info(message: str):
    logging.info(f"[TracingManager] {message}")

def log_error(message: str):
    logging.error(f"[TracingManager] {message}")
