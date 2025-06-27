import logging

def log_info(message: str):
    logging.info(f"[ConfigManager] {message}")

def log_error(message: str):
    logging.error(f"[ConfigManager] {message}")
