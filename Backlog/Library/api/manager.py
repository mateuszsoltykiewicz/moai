from fastapi import FastAPI
from .routers import get_all_routers
from .metrics import record_api_operation
from Library.logging import get_logger

logger = get_logger(__name__)

class ApiManager:
    """
    Central manager for API routers in the application.
    """
    def __init__(self):
        self.app: FastAPI = None
        self._registered_routers = []

    async def setup(self, app: FastAPI, config):
        """
        Async setup logic for the ApiManager.
        Registers all routers with the FastAPI app.
        """
        self.app = app
        try:
            routers = get_all_routers(config)
            for router in routers:
                self.app.include_router(router)
                self._registered_routers.append(router)
                record_api_operation("register_router")
                logger.info(f"ApiManager: Router {getattr(router, 'prefix', str(router))} registered.")
            logger.info("ApiManager: All routers registered.")
        except Exception as e:
            logger.error(f"ApiManager setup failed: {e}", exc_info=True)
            raise RuntimeError(f"ApiManager setup failed: {e}")

    async def shutdown(self):
        """
        Async shutdown logic for the ApiManager.
        """
        try:
            # If you have any shutdown hooks for routers, call them here
            logger.info("ApiManager: Shutdown complete.")
        except Exception as e:
            logger.error(f"ApiManager shutdown failed: {e}", exc_info=True)
            raise RuntimeError(f"ApiManager shutdown failed: {e}")

    async def register_router(self, router):
        """
        Register a single router dynamically.
        """
        try:
            self.app.include_router(router)
            self._registered_routers.append(router)
            record_api_operation("register_router")
            logger.info(f"ApiManager: Router {getattr(router, 'prefix', str(router))} registered dynamically.")
        except Exception as e:
            logger.error(f"Failed to register router {getattr(router, 'prefix', str(router))}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to register router: {e}")

    async def list_routers(self):
        """
        List all registered routers.
        """
        if not self.app:
            return []
        return [getattr(r, 'prefix', str(r)) for r in self._registered_routers]

    # Note: FastAPI does not support router removal natively.
    async def unregister_router(self, router):
        """
        Log request to unregister a router (not supported in FastAPI).
        """
        logger.warning(f"ApiManager: Unregister router {getattr(router, 'prefix', str(router))} requested but not supported.")
