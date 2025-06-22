"""
FastAPI Application Entry Point

- Dynamic router inclusion based on configuration
- TLS protection when enabled
- RBAC integration
- Comprehensive security headers
- Structured logging and observability
- Async lifespan management
- Custom exception handling
"""

import os
import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from api.middleware.security import SecurityMiddleware

# Import core modules
from core.config import AsyncConfigManager, AppConfig
from core.logging import configure_logging
from exceptions.core import (
    UnauthorizedError, ForbiddenError, 
    NotFoundError, ValidationError,
    ServiceUnavailableError
)
from api.dependencies import (
    get_current_user, require_role, 
    get_config_manager, endpoint_processor
)
from api.routers import (
    alarms, appstate, audit, auth, canbus, config as config_router, 
    database, events, health, i2c, kafka, logging as logging_router, 
    metrics, mtls, rate_limiting, secrets, tracing, updates
)

logger = logging.getLogger("api.main")

# Dynamic router registry
ROUTER_REGISTRY = {
    "alarms": alarms.router,
    "appstate": appstate.router,
    "audit": audit.router,
    "auth": auth.router,
    "canbus": canbus.router,
    "config": config_router.router,
    "database": database.router,
    "events": events.router,
    "health": health.router,
    "i2c": i2c.router,
    "kafka": kafka.router,
    "logging": logging_router.router,
    "metrics": metrics.router,
    "mtls": mtls.router,
    "rate_limiting": rate_limiting.router,
    "secrets": secrets.router,
    "tracing": tracing.router,
    "updates": updates.router
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for application lifecycle"""
    # Initialize configuration manager
    config_mgr = AsyncConfigManager("configs/app_config.json", schema=AppConfig)
    await config_mgr.start()
    app.state.config_mgr = config_mgr
    
    # Initialize logging
    config = await config_mgr.get()
    configure_logging(
        service_name=config.app.name,
        fluentd_host=config.logging.fluentd_host,
        fluentd_port=config.logging.fluentd_port
    )
    
    logger.info("Application starting up")
    
    # Yield control to the application
    yield
    
    # Shutdown procedures
    await config_mgr.stop()
    logger.info("Application shutting down")

def create_app() -> FastAPI:
    """Factory function to create and configure FastAPI app"""
    app = FastAPI(
        title="AppLib API",
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Security headers middleware
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
    
    # Logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    
    # Exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
    
    # Register custom exceptions
    app.add_exception_handler(UnauthorizedError, http_exception_handler)
    app.add_exception_handler(ForbiddenError, http_exception_handler)
    app.add_exception_handler(NotFoundError, http_exception_handler)
    app.add_exception_handler(ValidationError, http_exception_handler)
    app.add_exception_handler(ServiceUnavailableError, http_exception_handler)
    
    # Apply middleware
    app.add_middleware(SecurityMiddleware)
    
    return app

app = create_app()

@app.on_event("startup")
async def configure_app():
    """Final app configuration after creation"""
    config_mgr: AsyncConfigManager = app.state.config_mgr
    config = await config_mgr.get()
    
    # Enable HTTPS redirection if configured
    if config.security.https_redirect:
        app.add_middleware(HTTPSRedirectMiddleware)
        logger.info("HTTPS redirection enabled")
    
    # Include routers based on configuration
    for router_name, router in ROUTER_REGISTRY.items():
        if getattr(config.routers, router_name, False):
            app.include_router(router)
            logger.info(f"Included router: {router_name}")
    
    # Set up observability
    Instrumentator().instrument(app).expose(app)
    FastAPIInstrumentor.instrument_app(app)
    
    # Serve static files if configured
    if config.app.serve_static:
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("Static file serving enabled")

# Root endpoint with health check
@app.get("/")
async def root():
    return {"status": "running", "version": app.version}

# Example endpoint with RBAC and custom hooks
@app.get("/protected",
         dependencies=[Depends(require_role("admin"))],
         responses={
             200: {"description": "Successful response"},
             403: {"description": "Forbidden"},
             401: {"description": "Unauthorized"}
         })
async def protected_route(
    context: dict = Depends(
        lambda r: endpoint_processor(
            r,
            pre_hook="api.hooks.security.validate_request",
            post_hook="api.hooks.audit.log_access"
        )
    )
):
    """Example protected route with RBAC and hooks"""
    return {"message": "Access granted to protected resource"}

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration for server settings
    config_mgr = AsyncConfigManager("configs/app_config.json", schema=AppConfig)
    config = config_mgr.get()
    
    ssl_params = {}
    if config.security.tls.enabled:
        ssl_params = {
            "ssl_keyfile": config.security.tls.key_path,
            "ssl_certfile": config.security.tls.cert_path
        }
    
    uvicorn.run(
        "api.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
        **ssl_params
    )
