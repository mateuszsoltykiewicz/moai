import traceback
import asyncio
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from .schemas import ExceptionPayload
from .forwarder import forward_exception
from Library.logging import get_logger
from Library.metrics import record_exception_occurred

logger = get_logger(__name__)

class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as http_exc:
            # FastAPI's built-in HTTP exceptions
            return JSONResponse(
                status_code=http_exc.status_code,
                content={"detail": http_exc.detail}
            )
        except Exception as exc:
            # Generate payload
            payload = ExceptionPayload(
                type=type(exc).__name__,
                message=str(exc),
                stacktrace=traceback.format_exc(),
                service_name="your-service-name",  # Should be injected from config
                path=request.url.path,
                method=request.method,
                headers=dict(request.headers),
                timestamp=time.time()
            )
            
            # Log locally
            logger.error(f"Unhandled exception: {payload.dict()}")
            
            # Record metric
            record_exception_occurred(payload.type)
            
            # Forward asynchronously (non-blocking)
            asyncio.create_task(forward_exception(payload))
            
            # Return user-friendly response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
