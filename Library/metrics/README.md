# MetricsManager

## Purpose

The MetricsManager provides centralized Prometheus/OpenMetrics management for the application:

- Registers and exposes metrics for all components
- Provides async lifecycle management
- Integrates with FastAPI for /metrics endpoint

## Features

- Prometheus/OpenMetrics exporter
- Custom metric registry
- Counter, Gauge, Histogram, Summary support
- Async setup/shutdown

## API

- `GET /metrics` – Prometheus scrape endpoint

## Usage

Instantiate at app startup and inject into components as needed.
Register and use metrics via the manager.
