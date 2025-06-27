import logging

def log_info(message: str):
    logging.info(f"[RedisManager] {message}")

def log_error(message: str):
    logging.error(f"[RedisManager] ERROR: {message}")
