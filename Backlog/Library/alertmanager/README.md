# AlertManager Component

## Overview

Production-grade client for interacting with Prometheus AlertManager. Provides async methods for sending alerts, managing silences, and checking health status.

## Features

- Async HTTP client with automatic retries and exponential backoff
- Full support for AlertManager API (alerts, silences, health checks)
- Built-in Prometheus metrics for operations and latency
- Centralized logging via `Library.logging`
- Type safety with Pydantic models

## Key Methods

- `send_alert(alert: Alert)`: Send single alert
- `send_alerts(alerts: List[Alert])`: Send multiple alerts
- `get_alerts()`: Retrieve current alerts
- `create_silence(silence: Silence)`: Create new silence
- `get_silences()`: List active silences
- `health_check()`: Check AlertManager health

## Interactions

- **Library.logging**: All logging operations
- **Prometheus**: Exposes metrics via `ALERTMANAGER_OPERATIONS` and `ALERTMANAGER_LATENCY`
- **AlarmsServer**: Primary consumer for sending alerts

## Potential Improvements

- Add circuit breaker pattern for AlertManager outages
- Implement alert batching for high-volume scenarios
- Add more detailed health checks (e.g., cluster status)

## Potential Bug Sources

- Missing error handling in `_request` retry logic
- Type mismatches between Pydantic models and AlertManager API
- Connection leaks if `close()` is not called properly

## Logging

All errors and operations are logged through `Library.logging` with structured context.

## Usage Example

from Library.alertmanager import AlertManagerClient, Alert
client = AlertManagerClient(base_url="http://alertmanager:9093")
await client.send_alert(Alert(
labels={"alertname": "ServiceDown", "service": "payments"},
annotations={"summary": "Payment service unavailable"}
))
await client.close()
