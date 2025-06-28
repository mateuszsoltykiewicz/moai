# Grafana Integration Component

## Overview

Async, production-ready Grafana API client for dashboards, annotations, and alert queries.  
**Centralized logging and Prometheus metrics for all operations.**

## Features

- **Async HTTP Client**: Non-blocking, retry-enabled operations
- **API Token Authentication**: Secure access to Grafana APIs
- **Metrics**: Prometheus counters and histograms for all operations
- **Centralized Logging**: Uses `Library.logging` for all logs
- **Error Handling**: Full stack traces and error context

## Key Methods

- `get_dashboard(uid)`: Fetch dashboard by UID
- `push_annotation(annotation)`: Add annotation to Grafana
- `query_alerts()`: Query Grafana alerts
- `health_check()`: Check Grafana API health

## Usage Example

from Library.grafana.client import GrafanaClient, Annotation
grafana = GrafanaClient(base_url="http://grafana:3000", api_token="YOUR_TOKEN")
dashboard = await grafana.get_dashboard(uid="abc123")
await grafana.push_annotation(Annotation(time=..., text="Deployment started"))
alerts = await grafana.query_alerts()
await grafana.close()

## Interactions

- **Grafana API**: For dashboards, annotations, alerts
- **Library.logging**: Centralized logging for all operations
- **Library.metrics**: Prometheus metrics for all operations

## Potential Improvements

- Add support for folder and datasource management
- Implement alert rule creation/update APIs
- Add circuit breaker for Grafana outages

## Potential Bug Sources

1. **Token Expiry**: Expired API token will cause authentication failures
2. **Network Issues**: Lost connectivity to Grafana will raise errors
3. **Schema Drift**: Grafana API changes may break response parsing

## Logging

All operations use `Library.logging` with structured JSON format. Errors include full stack traces.
