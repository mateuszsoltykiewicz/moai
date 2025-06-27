import logging
import time

def log_info(message: str):
    logging.info(f"[I2C] {message}")

def log_error(message: str):
    logging.error(f"[I2C] ERROR: {message}")

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start
        log_info(f"{func.__name__} executed in {duration:.4f}s")
        return result
    return wrapper
