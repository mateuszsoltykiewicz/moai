# DisasterDetector

## Overview

DisasterDetector monitors FATAL alarms and sensor data to detect and report disasters (e.g., water overheat). It is a core reliability service for the platform.

## Features

- Monitors FATAL alarms from AlarmsServer (API or Kafka)
- Produces to `DisasterDetected` Kafka topic
- Consumes from `sensorData` (with filtering)
- Only monitors water temperature if HeatingJob is running
- Maintains disaster state in StateServer
- Clears disaster-specific alarms on startup
- Crashes on FATAL alarm (manual restart required)
- Integrates with AlarmsServer, StateServer, ConfigurationServer
- Full metrics, tracing, health endpoints
- mTLS and JWT/OIDC security

## API Endpoints

| Endpoint           | Method | Description                | Security (Required)  |
|--------------------|--------|----------------------------|----------------------|
| `/disaster/status` | GET    | Get disaster status        | JWT/OIDC, RBAC       |

## Kafka Topics

| Topic             | Direction | Description                |
|-------------------|-----------|----------------------------|
| `DisasterDetected`| Produce   | Disaster detection events  |
| `sensorData`      | Consume   | Input sensor data          |

## Security

All endpoints require:

- mTLS client certificates
- Valid JWT with RBAC permissions
- `disaster:read` for GET endpoints

## Health Checks

- `/health/live`: Liveness
- `/health/ready`: Readiness

## Failure Mode

- **FATAL Alarm**: Immediately crashes service (`sys.exit(1)`)

## Metrics

- `disaster_detections_total`

## Last Updated

2025-06-28
