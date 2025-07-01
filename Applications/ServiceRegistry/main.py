import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from Library.logging import setup_logging
from Library.metrics import setup_metrics
from Library.tracing import setup_tracing
from Library.exceptions import ExceptionHandlingMiddleware
from Library.api import get_health_router
from .api import router as registry_router
from .manager import ServiceRegistryManager

logger = setup_logging(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ServiceRegistry...")
    setup_metrics()
    setup_tracing(service_name="ServiceRegistry")
    await ServiceRegistryManager.setup()
    logger.info("ServiceRegistry started successfully")
    yield
    logger.info("Shutting down ServiceRegistry...")
    await ServiceRegistryManager.shutdown()
    logger.info("ServiceRegistry shutdown complete")

app = FastAPI(
    title="ServiceRegistry",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(ExceptionHandlingMiddleware)
app.include_router(get_health_router())
app.include_router(registry_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
