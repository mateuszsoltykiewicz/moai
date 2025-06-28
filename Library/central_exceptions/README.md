# Central Exceptions Component

## Overview

Centralized exception management system for aggregating, storing, and analyzing exceptions from all microservices. 
Provides secure, authenticated API endpoints for exception submission, querying, and statistics.

## Features

- **Global Exception Aggregation**: Collects exceptions from all microservices
- **Persistent Storage**: Stores exceptions in a database for analysis
- **Query API**: Filter exceptions by type, service, and time
- **Alerting Integration**: Optional alerting on critical exceptions
- **JWT/OIDC Security**: All endpoints require valid Keycloak-issued JWTs
- **RBAC Enforcement**: Fine-grained access control for read/write operations
- **Prometheus Metrics**: Tracks exception processing and query operations
- **Centralized Logging**: Uses `Library.logging` for all logs

## API Endpoints

| Endpoint           | Method | Description                      | Security (Required)  |
|--------------------|--------|----------------------------------|----------------------|
| `/exceptions/submit` | POST   | Submit an exception payload      | JWT/OIDC, RBAC       |
| `/exceptions/query`  | GET    | Query exceptions with filters    | JWT/OIDC, RBAC       |
| `/exceptions/stats`  | GET    | Get aggregated exception stats   | JWT/OIDC, RBAC       |

## Usage Example

Submit an exception

await central_exceptions_manager.process_exception(ExceptionPayload(
type="ValueError",
message="Invalid input",
stacktrace="Traceback (most recent call last): ...",
service_name="payment-service",
path="/payments",
method="POST",
headers={"user-agent": "test-client"},
timestamp=1698765432.123
))
Query exceptions

exceptions = await central_exceptions_manager.query_exceptions(
exception_type="ValueError",
service_name="payment-service",
limit=50
)
Get stats

stats = await central_exceptions_manager.get_stats()

## Interactions

- **Library.database**: For persistent exception storage
- **Library.alerting**: For sending alerts on critical exceptions
- **Library.api.security**: For JWT/OIDC validation and RBAC
- **Library.logging**: Centralized logging for all operations
- **Library.metrics**: Metrics collection for exception operations

## Security

- All API endpoints enforce JWT/OIDC authentication and RBAC authorization
- No unauthenticated access is permitted
- Sensitive exception data is protected and logged securely

## Potential Improvements

- Add exception aggregation and deduplication
- Implement alerting rules for specific exception types
- Add exception retention policies and archival
- Provide UI/dashboard for exception analysis

## Potential Bug Sources

1. **Database Performance**: High volume of exceptions may impact DB performance
2. **Alerting Overload**: Excessive alerts may cause noise
3. **Security Leaks**: Improper access control may expose sensitive data
4. **Data Consistency**: Partial writes or failures may cause data loss

## Logging

All operations use `Library.logging` with structured JSON format. Exception details are logged with care to avoid sensitive data exposure.

## Last Updated

2025-06-28
