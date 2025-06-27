import logging

def log_info(message: str):
    logging.info(f"[Secrets] {message}")

def log_error(message: str):
    logging.error(f"[Secrets] ERROR: {message}")

def log_debug(message: str):
    logging.debug(f"[Secrets] {message}")
