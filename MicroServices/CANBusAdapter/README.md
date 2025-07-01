# CANBusAdapter

## Overview

CANBusAdapter integrates with Raspberry Pi GPIO to ingest CAN bus sensor data, produces events, and manages CANBus-specific alarms. It is a core adapter for the platform.

## Features

- Polls CAN bus and produces to `sensorData` topic
- Produces `createAlarm` and `deleteAlarm` as needed
- Maintains sensor data in DB and state
- Clears CANBus alarms on startup
- Crashes on FATAL alarm
- Integrates with AlarmsServer, StateServer, ConfigurationServer
- Full metrics, tracing, health endpoints
- mTLS and JWT/OIDC security

## API Endpoints

| Endpoint             | Method | Description             | Security (Required)  |
|----------------------|--------|-------------------------|----------------------|
| `/canbus/sensor-data`| GET    | Get latest sensor data  | JWT/OIDC, RBAC       |

## Kafka Topics

| Topic         | Direction | Description                |
|---------------|-----------|----------------------------|
| `sensorData`  | Produce   | Output sensor data         |
| `createAlarm` | Produce   | Alarm creation events      |
| `deleteAlarm` | Produce   | Alarm resolution events    |

## Security

All endpoints require:

- mTLS client certificates
- Valid JWT with RBAC permissions
- `canbus:read` for GET endpoints

## Health Checks

- `/health/live`: Liveness
- `/health/ready`: Readiness

## Failure Mode

- **FATAL Alarm**: Immediately crashes service (`sys.exit(1)`)

## Metrics

- `canbus_polls_total`

## Last Updated

2025-06-28
