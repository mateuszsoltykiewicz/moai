import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from Library.logging import setup_logging
from Library.metrics import setup_metrics
from Library.tracing import setup_tracing
from Library.exceptions import ExceptionHandlingMiddleware
from Library.api import get_health_router
from .manager import BankManager

logger = setup_logging(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting BankManager...")
    setup_metrics()
    setup_tracing(service_name="BankManager")
    await BankManager.setup()
    logger.info("BankManager started successfully")
    yield
    logger.info("Shutting down BankManager...")
    await BankManager.shutdown()
    logger.info("BankManager shutdown complete")

app = FastAPI(
    title="BankManager",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(ExceptionHandlingMiddleware)
app.include_router(get_health_router())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
