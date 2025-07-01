# AlarmsServer

## Overview

AlarmsServer manages alarm lifecycle, history, and triggers in the platform. It consumes `createAlarm` and `deleteAlarm` Kafka topics, maintains alarm state and history, and integrates with I2CAdapter for power cut-off on FATAL alarms.

## Features

- Consumes `createAlarm` and `deleteAlarm` Kafka topics
- Maintains full alarm history (soft delete)
- Stores operational state in StateServer
- Fetches config from ConfigurationServer with hot-reload
- Exposes Prometheus metrics, OpenTelemetry tracing, health endpoints
- Supports secrets rotation via Vault
- APIs protected by mTLS and JWT/OIDC with RBAC
- Acts as backend for HomeKit/iPhone alarm reporting
- Triggers power cut-off relay via I2CAdapter on FATAL alarms

## API Endpoints

| Endpoint           | Method | Description           | Security (Required)  |
|--------------------|--------|-----------------------|----------------------|
| `/alarms/create`   | POST   | Create a new alarm    | JWT/OIDC, RBAC       |
| `/alarms/delete`   | POST   | Soft-delete an alarm  | JWT/OIDC, RBAC       |
| `/alarms/current`  | GET    | Get current active alarms | JWT/OIDC, RBAC    |

## Security

All endpoints require:

- mTLS client certificates
- Valid JWT with RBAC permissions
- `alarms:write` for POST endpoints
- `alarms:read` for GET endpoints

## Health Checks

- `/health/live`: Liveness check
- `/health/ready`: Readiness check

## Metrics

- `alarms_operations_total`

## Logging

All operations use centralized structured logging via `Library.logging`.

## Last Updated

2025-06-28
