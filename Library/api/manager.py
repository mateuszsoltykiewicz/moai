"""
ApiManager: Centralized API router and lifecycle management.

- Registers and manages all FastAPI routers for the application
- Supports dynamic router registration and dependency injection
- Integrates with OpenAPI docs, metrics, and logging
"""

from fastapi import FastAPI
from .routers import get_all_routers
from .utils import log_info

class ApiManager:
    """
    Central manager for API routers in the application.
    """
    def __init__(self):
        self.app: FastAPI = None

    async def setup(self, app: FastAPI):
        """
        Async setup logic for the ApiManager.
        Registers all routers with the FastAPI app.
        """
        self.app = app
        for router in get_all_routers():
            self.app.include_router(router)
        log_info("ApiManager: All routers registered.")

    async def shutdown(self):
        """
        Async shutdown logic for the ApiManager.
        """
        log_info("ApiManager: Shutdown complete.")
