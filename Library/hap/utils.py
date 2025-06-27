import logging

def log_info(message: str):
    logging.info(f"[HAP] {message}")

def log_error(message: str):
    logging.error(f"[HAP] ERROR: {message}")

def log_debug(message: str):
    logging.debug(f"[HAP] {message}")
