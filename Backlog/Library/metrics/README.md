# Metrics Component

## Overview

Centralized Prometheus/OpenMetrics management for all microservices.  
Exposes a `/metrics` endpoint for Prometheus scrapes and provides reusable, thread-safe metric registration and recording for all components.

## Features

- **Centralized Metrics Registry**: All metrics registered in a single Prometheus registry.
- **Async Lifecycle**: Setup and shutdown hooks for integration with application lifecycle.
- **Custom Metrics Support**: Register counters, gauges, histograms, and summaries with custom labels.
- **Prometheus Endpoint**: `/metrics` endpoint for scraping by Prometheus.
- **Reusable Metric Definitions**: General operation counters and histograms for cross-component use.
- **Centralized Logging**: Uses `Library.logging` for all logs and error reporting.
- **Exception Handling**: Custom exceptions for registration and scrape errors.

## API Endpoints

| Endpoint      | Method | Description                | Security (Required) |
|---------------|--------|----------------------------|---------------------|
| `/metrics`    | GET    | Prometheus scrape endpoint | None (public)       |

## Requirements

- Prometheus Python client (`prometheus_client`)
- FastAPI for API integration

## Usage Example

from Library.metrics.manager import MetricsManager
metrics_manager = MetricsManager()
await metrics_manager.setup()
Register a custom counter

counter = await metrics_manager.register_counter(
name="my_counter",
description="Custom counter",
labelnames=["service"]
)
counter.labels(service="my-service").inc()
Expose metrics via FastAPI

from Library.metrics.api import router as metrics_router
app.include_router(metrics_router)

## Interactions

- **Prometheus**: For metrics scraping and monitoring.
- **All Components**: Register and use metrics via this manager.
- **Library.logging**: For all operational logs and error reporting.

## Security

- The `/metrics` endpoint is public by default (as per Prometheus best practices).
- Sensitive data should never be included in metric labels or values.

## Potential Improvements

- Add authentication option for `/metrics` endpoint.
- Support for pushgateway integration.
- Add metric auto-discovery and documentation endpoints.

## Potential Bug Sources

- **Metric Name Collisions**: Registering the same metric name multiple times.
- **Improper Label Usage**: Using variable or high-cardinality labels may overload Prometheus.
- **Registry Leaks**: Not unregistering metrics on shutdown.
- **Scrape Failures**: Large or slow metrics may cause Prometheus scrape timeouts.

## Logging

- All registration and scrape operations are logged via `Library.logging`.
- Errors include stack traces (`exc_info=True`) for troubleshooting.

## Last Updated

2025-06-28
