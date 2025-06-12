"""
Main FastAPI app for the platform.

- Dynamically includes routers based on config (hot reload supported)
- API versioning: all routes are under /api/v1/
- Standardized error handling and security headers
- Integrated with secrets and auth subservices
- Ready for observability (tracing, metrics) and extension
"""

import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from core.logging import configure_logging
from core.config import get_settings
from prometheus_fastapi_instrumentator import Instrumentator
from core.config import AsyncConfigManager
from models.config import AppConfig
from models.schemas import ErrorResponseSchema
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry import trace

# Import all routers (add as needed)
from api.routers import (
    alarms, appstate, audit, auth, canbus, config as config_router, database, events, health,
    i2c, kafka, logging as logging_router, metrics, mtls, rate_limiting, secrets,
    tracing, updates
)

# Import dependencies for secrets and auth initialization
from api.dependencies import get_secrets_manager, get_auth_service

API_PREFIX = "/api/v1"

settings = get_settings()
configure_logging(
    service_name=settings.app_name,
    fluentd_host=settings.fluentd_host,
    fluentd_port=settings.fluentd_port
)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
)
instrumentator.instrument(app).expose(app, endpoint="/metrics")

# Configure Jaeger exporter (or Zipkin, OTLP, etc.)
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",  # set via env or config
    agent_port=6831,
)

resource = Resource(attributes={"service.name": "my-fastapi-service"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(jaeger_exporter)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# --- Security Headers Middleware ---
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

# --- Standardized API Exception ---
class APIException(Exception):
    def __init__(self, status_code: int, message: str, details: dict = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}

async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponseSchema(
            error=exc.message,
            details=exc.details
        ).dict()
    )

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Platform API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# --- Middleware ---
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add tracing/logging/metrics middleware as needed

# --- Optional Routers Mapping ---
OPTIONAL_ROUTERS = {
    "canbus": canbus.router,
    "database": database.router,
    "i2c": i2c.router,
    "kafka": kafka.router,
}

# --- Always-Included Routers ---
ALWAYS_INCLUDED_ROUTERS = [
    (alarms.router, "alarms"),
    (appstate.router, "appstate"),
    (audit.router, "audit"),
    (auth.router, "auth"),
    (config_router.router, "config"),
    (events.router, "events"),
    (health.router, "health"),
    (logging_router.router, "logging"),
    (metrics.router, "metrics"),
    (mtls.router, "mtls"),
    (rate_limiting.router, "rate_limiting"),
    (secrets.router, "secrets"),
    (tracing.router, "tracing"),
    (updates.router, "updates"),
]

def include_routers_from_config(app, routers_config):
    """
    Dynamically include/exclude routers based on config.
    """
    current_paths = {route.path for route in app.router.routes}
    # Always-included routers
    for router, tag in ALWAYS_INCLUDED_ROUTERS:
        app.include_router(router, prefix=f"{API_PREFIX}/{tag}", tags=[tag])
    # Optional routers
    for name, router in OPTIONAL_ROUTERS.items():
        router_paths = {route.path for route in router.routes}
        if getattr(routers_config, name, False):
            if not router_paths & current_paths:
                app.include_router(router, prefix=f"{API_PREFIX}/{name}", tags=[name])
        else:
            app.router.routes = [
                route for route in app.router.routes if route.path not in router_paths
            ]
    # Regenerate OpenAPI schema for docs
    app.openapi_schema = None
    app.openapi()

# --- Startup Event: Load Config and Include Routers ---
@app.on_event("startup")
async def startup_event():
    """
    Initialize config manager, secrets manager, and auth service.
    """
    # Initialize config manager
    app.state.config_mgr = AsyncConfigManager("configs/dev/app_config.json", schema=AppConfig)
    await app.state.config_mgr.start()

    app.state.i2c_adapters = {}

    # Initialize secrets manager and auth service, store in app.state for global access
    app.state.secrets_manager = await get_secrets_manager()
    app.state.auth_service = await get_auth_service()

    app_config = await app.state.config_mgr.get()
    include_routers_from_config(app, app_config.routers)

    # Register config change listener for hot reload
    async def on_config_change(new_config):
        include_routers_from_config(app, new_config.routers)
    app.state.config_mgr.add_listener("router_manager", on_config_change)

    logging.info("API started with dynamic router inclusion and secure subservices.")

# --- Shutdown Event: Clean up config manager and secrets manager ---
@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up all background services and managers.
    """
    if hasattr(app.state, "secrets_manager"):
        await app.state.secrets_manager.stop()
    await app.state.config_mgr.stop()

# --- Register Error Handler ---
app.add_exception_handler(APIException, api_exception_handler)

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)


app = FastAPI()
FastAPIInstrumentor.instrument_app(app)