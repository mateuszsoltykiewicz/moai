# Health Component

## Overview

Production-grade health monitoring system with concurrent checks, timeouts, and detailed reporting.  
**All endpoints require JWT/OIDC authentication and authorization via the generic dependency.**

## Features

- **Concurrent Health Checks**: Runs multiple checks simultaneously
- **Timeout Protection**: Prevents slow checks from blocking the system
- **Degraded State Detection**: Differentiates between failed and degraded states
- **Metrics Integration**: Tracks check counts and durations
- **Centralized Logging**: Uses `Library.logging` component
- **Security**: JWT/OIDC enforcement for readiness endpoint

## API Endpoints

| Endpoint       | Method | Description                  | Security (Required)  |
|----------------|--------|------------------------------|----------------------|
| `/health/livez`| GET    | Basic liveness probe         | None (public)        |
| `/health/readyz`| GET    | Comprehensive readiness check | JWT/OIDC, RBAC       |

## Health Check Statuses

- `ok`: Component is healthy
- `degraded`: Component is functional but impaired
- `fail`: Component is non-functional
- `timeout`: Check exceeded time limit

## Usage Example

Register a health check

async def database_check():
return {"status": "ok", "details": {"connections": 5}}
health_manager.register_health_check("database", database_check)
Get health status

status = await health_manager.get_health_status()

## Potential Improvements

- Add historical health data tracking
- Implement automatic remediation for failed checks
- Add webhook notifications for status changes

## Potential Bug Sources

1. **Check Dependencies**: Slow checks may cause timeouts
2. **Thread Safety**: Concurrent registration of checks not thread-safe
3. **Error Handling**: Unhandled exceptions in checks may crash manager
4. **Stale State**: Cached health state may not reflect current status

## Security Best Practices

- Keep liveness endpoint public but minimal
- Restrict readiness endpoint to authenticated users
- Rotate JWT signing keys regularly
- Monitor health check metrics for anomalies

## Logging

All operations use `Library.logging` with structured JSON format. Failed checks include stack traces via `exc_info=True`.
