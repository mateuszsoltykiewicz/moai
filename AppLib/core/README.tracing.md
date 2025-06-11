# Async Tracing

## Overview

`core/tracing.py` provides async distributed tracing using OpenTelemetry.
- Easy integration with async/await code
- Works with Jaeger, Tempo, and other OTLP-compatible backends
- No-op fallback if tracing is disabled

## Usage

from core.tracing import AsyncTracer
tracer = AsyncTracer(“myservice”)
  async with tracer.start_span(“operation”, 
    {“custom”: “value”}
  ):
  await do_async_work()

## Configuration

- Set `TRACING_ENABLED=1` to enable tracing (default if OpenTelemetry is installed)
- Set `OTEL_EXPORTER_OTLP_ENDPOINT` to your collector endpoint

## Requirements

- opentelemetry-api
- opentelemetry-sdk
- opentelemetry-exporter-otlp-proto-grpc

Install with:

pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc
