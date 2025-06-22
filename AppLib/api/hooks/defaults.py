"""
Default hook implementations
"""

from fastapi import Request
from core.logging import logger
from metrics.core import record_endpoint_metrics
import time

async def default_pre_hook(request: Request):
    """Default pre-hook: log request start"""
    logger.info(f"Request started: {request.method} {request.url}")
    return {"start_time": time.monotonic()}

async def default_post_hook(request: Request, response, context):
    """Default post-hook: log request completion"""
    duration = time.monotonic() - context.get("start_time", time.monotonic())
    logger.info(f"Request completed: {request.method} {request.url} - {response.status_code} ({duration:.2f}s)")
    
    # Record metrics
    record_endpoint_metrics(
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration=duration
    )

# Register default hooks
from api.hooks.registry import hook_registry
hook_registry.register("default_pre_hook", default_pre_hook)
hook_registry.register("default_post_hook", default_post_hook)
