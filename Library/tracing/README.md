# TracingManager

## Purpose

The TracingManager provides centralized OpenTelemetry tracing for the application:

- Configures and exposes a global tracer for all components
- Supports dynamic exporter and resource configuration
- Integrates with FastAPI and other frameworks

## Features

- OpenTelemetry exporter (OTLP, console)
- Async setup/shutdown
- API for diagnostics and test spans

## API

- `GET /tracing/test-span` – Generate and return a test trace span
- `GET /tracing/info` – Tracing diagnostics and exporter status

## Usage

Instantiate at app startup and inject into components as needed.
Use `tracing_manager.get_tracer()` to instrument your code.
