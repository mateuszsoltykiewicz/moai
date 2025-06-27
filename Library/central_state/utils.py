import logging

def log_info(message: str):
    logging.info(f"[CentralStateRegistry] {message}")

def log_error(message: str):
    logging.error(f"[CentralStateRegistry] ERROR: {message}")
