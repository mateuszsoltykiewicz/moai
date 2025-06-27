import logging

def log_info(message: str):
    logging.info(f"[ApiManager] {message}")

def log_error(message: str):
    logging.error(f"[ApiManager] {message}")
