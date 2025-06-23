"""
UtilsManager: Centralized utility and helper management.

- Provides logging, formatting, and common helpers
- Exposes async lifecycle management
- Integrates with FastAPI and all components
"""

import logging
from .logging import setup_logging

class UtilsManager:
    def __init__(self):
        self.logger = None

    async def setup(self, config: dict = None):
        """
        Async setup logic for the UtilsManager.
        """
        self.logger = setup_logging(config)
        self.logger.info("UtilsManager: Setup complete.")

    async def shutdown(self):
        """
        Async shutdown logic for the UtilsManager.
        """
        if self.logger:
            self.logger.info("UtilsManager: Shutdown complete.")

    def get_logger(self, name: str = "app"):
        """
        Get a logger instance.
        """
        return logging.getLogger(name)
