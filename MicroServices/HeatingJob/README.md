# HeatingJob

## Overview

HeatingJob is an orchestrated microservice responsible for controlling heating cycles, monitoring temperature, and raising/clearing alarms. It is triggered by Kubernetes or a controller, integrates with sensor data, and ensures heating safety.

## Features

- Triggered by K8s API or controller
- Produces to `I2CHeating` Kafka topic
- Consumes from `sensorData` (filtered)
- Maintains job state in StateServer
- Raises/clears alarms via AlarmsServer
- Fails with exit code 1 if temperature doesn't change in time
- Crashes immediately on FATAL alarm
- Fetches config from ConfigurationServer with hot-reload
- Full metrics, tracing, health, secrets, and state support
- mTLS and JWT/OIDC security

## API Endpoints

| Endpoint            | Method | Description             | Security (Required)  |
|---------------------|--------|-------------------------|----------------------|
| `/heating/trigger`  | POST   | Trigger heating job     | JWT/OIDC, RBAC       |
| `/heating/status`   | GET    | Get heating job status  | JWT/OIDC, RBAC       |

## Kafka Topics

| Topic        | Direction | Description                |
|--------------|-----------|----------------------------|
| `I2CHeating` | Produce   | Heating control events     |
| `sensorData` | Consume   | Input sensor data          |

## Security

All endpoints require:

- mTLS client certificates
- Valid JWT with RBAC permissions
- `heating:write` for POST endpoints
- `heating:read` for GET endpoints

## Health Checks

- `/health/live`: Liveness
- `/health/ready`: Readiness

## Failure Mode

- **FATAL Alarm**: Immediately crashes service (`sys.exit(1)`)
- **No Temp Change**: Fails with exit code 1 and raises FATAL alarm

## Metrics

- `heating_job_operations_total`

## Last Updated

2025-06-28
