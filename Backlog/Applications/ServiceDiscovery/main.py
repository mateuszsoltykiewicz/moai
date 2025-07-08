import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from Library.logging import setup_logging
from Library.metrics import setup_metrics
from Library.tracing import setup_tracing
from Library.exceptions import ExceptionHandlingMiddleware
from Library.api import get_health_router
from .api import router as discovery_router
from .manager import ServiceDiscoveryManager

logger = setup_logging(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ServiceDiscovery...")
    setup_metrics()
    setup_tracing(service_name="ServiceDiscovery")
    await ServiceDiscoveryManager.setup()
    logger.info("ServiceDiscovery started successfully")
    yield
    logger.info("Shutting down ServiceDiscovery...")
    await ServiceDiscoveryManager.shutdown()
    logger.info("ServiceDiscovery shutdown complete")

app = FastAPI(
    title="ServiceDiscovery",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(ExceptionHandlingMiddleware)
app.include_router(get_health_router())
app.include_router(discovery_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
