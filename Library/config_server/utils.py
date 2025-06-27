import logging

def log_info(message: str):
    logging.info(f"[ConfigServer] {message}")

def log_error(message: str):
    logging.error(f"[ConfigServer] ERROR: {message}")
