"""
Observability middleware for metrics, logging, and tracing
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from metrics.core import record_endpoint_metrics
from core.logging import logger
from opentelemetry import trace
import time

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.monotonic()
        
        # Create span for distributed tracing
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(f"{request.method} {request.url.path}"):
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.monotonic() - start_time
            
            # Record metrics
            record_endpoint_metrics(
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration=duration
            )
            
            # Log completion
            logger.info(f"{request.method} {request.url.path} - {response.status_code} ({duration:.2f}s)")
            
            return response
