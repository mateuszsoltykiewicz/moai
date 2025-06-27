import logging
import time

def log_info(message: str):
    logging.info(f"[Kafka] {message}")

def log_error(message: str):
    logging.error(f"[Kafka] ERROR: {message}")

def log_warning(message: str):
    logging.warning(f"[Kafka] WARN: {message}")
