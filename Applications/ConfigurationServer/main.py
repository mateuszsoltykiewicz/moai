import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from Library.logging import setup_logging
from Library.metrics import setup_metrics
from Library.tracing import setup_tracing
from Library.exceptions import ExceptionHandlingMiddleware
from Library.api import get_health_router
from .manager import ConfigServerManager
from .api import router as config_router

logger = setup_logging(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async lifespan manager for resource initialization and cleanup"""
    # Startup
    logger.info("Starting ConfigurationServer...")
    setup_metrics()
    setup_tracing(service_name="ConfigurationServer")
    await ConfigServerManager.setup()
    logger.info("ConfigurationServer started successfully")
    yield
    # Shutdown
    logger.info("Shutting down ConfigurationServer...")
    await ConfigServerManager.shutdown()
    logger.info("ConfigurationServer shutdown complete")

app = FastAPI(
    title="ConfigurationServer",
    version="1.0.0",
    lifespan=lifespan
)

# Add global exception middleware
app.add_middleware(ExceptionHandlingMiddleware)

# Include routers
app.include_router(get_health_router())
app.include_router(config_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
