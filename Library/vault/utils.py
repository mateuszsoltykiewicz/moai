import logging

def log_info(message: str):
    logging.info(f"[Vault] {message}")

def log_error(message: str):
    logging.error(f"[Vault] ERROR: {message}")
