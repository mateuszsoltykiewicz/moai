# Exceptions Component

## Overview

Production-grade exception handling for microservices. Catches all unhandled exceptions, logs them locally, records metrics, and forwards to a central ExceptionsServer. Fully integrated with FastAPI middleware.

## Features

- **Global Exception Handling**: Catches all unhandled exceptions via FastAPI middleware
- **Structured Payload**: Standardized exception schema with stacktrace and context
- **Async Forwarding**: Non-blocking exception forwarding with retry logic
- **Metrics Integration**: Tracks exception types via Prometheus
- **Fallback Mechanism**: Local logging if forwarding fails
- **Security**: JWT authentication for exception forwarding

## Installation

1. Add middleware to your FastAPI app:

from Library.exceptions import ExceptionHandlingMiddleware
app = FastAPI()
app.add_middleware(ExceptionHandlingMiddleware)

## Configuration

Set these environment variables:

- `EXCEPTION_SERVER_URL`: Central exceptions endpoint
- `EXCEPTION_SERVER_TOKEN`: JWT for authentication

## Exception Payload

{
  "type": "ValueError",
  "message": "Invalid input",
  "stacktrace": "...",
  "service_name": "payment-service",
  "path": "/payments",
  "method": "POST",
  "headers": {...},
  "timestamp": 1698765432.123,
  "context": {"user_id": "usr-123"}
}

## Security

- All forwarded exceptions use JWT authentication
- Sensitive data (tokens, credentials) is automatically redacted
- HTTPS enforced for all exception forwarding

## Metrics

- `exceptions_occurred_total`: Counter for exception types

## Best Practices

1. **Add Context**: Enhance payload with business context where possible

payload.context = {"order_id": "ord-123", "amount": 5000}

2. **Redact Sensitive Data**:

In middleware before forwarding

if "authorization" in payload.headers:
payload.headers["authorization"] = "REDACTED"

3. **Critical Exceptions**: Immediately alert on database connection failures

4. **Testing**: Verify forwarding with test exceptions in development

## Interactions

- **Central ExceptionsServer**: Forwards exception payloads
- **Library.logging**: Local exception logging
- **Library.metrics**: Exception type tracking
- **Library.config**: Server URL and token configuration

## Potential Improvements

- Add circuit breaker for exception server outages
- Implement payload compression for large stacktraces
- Add distributed tracing correlation IDs

## Last Updated

2025-06-28
