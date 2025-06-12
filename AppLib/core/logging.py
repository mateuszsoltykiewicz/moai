import logging
from logging.config import dictConfig
from fluent.handler import FluentHandler

def configure_logging(service_name: str, fluentd_host: str = 'localhost', fluentd_port: int = 24224):
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s"
            }
        },
        "handlers": {
            "fluentd": {
                "()": FluentHandler,
                "formatter": "json",
                "tag": f"{service_name}.app",
                "host": fluentd_host,
                "port": fluentd_port,
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "level": "INFO"
            }
        },
        "root": {
            "handlers": ["console", "fluentd"],
            "level": "INFO"
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False
            },
            "uvicorn.error": {
                "level": "WARNING",
                "propagate": False
            },
            "app": {
                "handlers": ["console", "fluentd"],
                "level": "INFO",
                "propagate": False
            }
        }
    }
    dictConfig(LOGGING_CONFIG)
