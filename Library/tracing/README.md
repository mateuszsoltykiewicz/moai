# Tracing Component

## Overview

Production-grade distributed tracing implementation using OpenTelemetry.  
**All API endpoints require JWT/OIDC authentication and RBAC authorization.**

## Features

- **OpenTelemetry Integration**: Standards-based tracing implementation
- **Multiple Exporters**: Supports OTLP (Jaeger, Zipkin) and console
- **Context Propagation**: Inject/extract trace context across services
- **Centralized Logging**: Uses `Library.logging` component
- **Metrics Integration**: Tracks trace collection and export
- **JWT/OIDC Security**: All endpoints require authentication

## API Endpoints

| Endpoint       | Method | Description                  | Security (Required)  |
|----------------|--------|------------------------------|----------------------|
| `/tracing/status` | GET  | Get tracing status          | JWT/OIDC, RBAC       |
| `/tracing/query` | GET  | Query traces (stub)         | JWT/OIDC, RBAC       |

## Key Components

| Component         | Purpose                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `TracingManager`  | Core tracing setup and span management                                  |
| `api.py`          | FastAPI endpoints with security enforcement                             |
| `schemas.py`      | Pydantic models for trace responses                                     |
| `metrics.py`      | Prometheus metrics for tracing operations                               |

## Usage Example

Initialize tracing

tracing_manager = TracingManager(
service_name="payment-service",
otlp_endpoint="http://jaeger:4318/v1/traces"
)
await tracing_manager.setup()
Create span

with tracing_manager.start_span("process-payment") as span:
span.set_attribute("user_id", "user-123")

# Business logic

Inject context into headers

headers = tracing_manager.inject_context({})

## Security

- **JWT/OIDC Validation**: Uses `Library/api/security` dependency
- **RBAC Enforcement**: Requires `tracing:read` for all endpoints
- **No Unauthenticated Access**: All endpoints require valid JWT

## Interactions

- **Jaeger/Zipkin**: For trace storage and visualization
- **Library.api.security**: JWT/OIDC validation and RBAC
- **Library.logging**: Centralized logging for all operations
- **All Microservices**: Create and propagate spans

## Potential Improvements

- Add sampling configuration
- Implement trace ID injection in logs
- Add span event recording
- Implement baggage propagation

## Potential Bug Sources

1. **Context Propagation**: Improper context handling breaks traces
2. **Exporter Failures**: Network issues may prevent trace export
3. **Performance Overhead**: High trace volume may impact performance
4. **Clock Drift**: Time synchronization issues across services

## Security Best Practices

- Secure OTLP endpoints with mTLS
- Restrict trace query access to authorized users
- Sanitize span attributes for sensitive data

## Logging

All operations use `Library.logging` with structured JSON format.  
Trace IDs are logged, but sensitive span attributes are omitted.

## Last Updated

2025-06-28
