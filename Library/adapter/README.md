# Adapter Component

## Overview

Centralized, async management system for hardware/software adapters. Supports dynamic registration, retrieval, and lifecycle management of adapters, with full integration into your platform’s metrics and centralized logging stack.

## Features

- Dynamic adapter registration and discovery
- Singleton management per adapter type
- Async lifecycle support (`async_setup`, `async_teardown`)
- Thread-safe operations with asyncio locks
- Prometheus metrics for operations and latency
- Centralized logging via `Library.logging`

## API Endpoints

| Endpoint       | Method | Description                          | Response Model       |
|----------------|--------|--------------------------------------|----------------------|
| `/adapter/`    | POST   | Create/retrieve adapter instance     | `AdapterInfo`        |
| `/adapter/`    | GET    | List registered adapter types        | `Dict[str, str]`     |

## Interactions

- **Uses Library.logging** for all logging (no ad-hoc logging)
- **Uses Library.metrics** for Prometheus metrics
- **Works with adapters from i2c, kafka, database, canbus, etc.**
- **Should register with service discovery if required by your architecture**

## Potential Improvements

- Add health checks for adapters (monitor status in metrics)
- Add configuration validation for adapter configs

## Potential Bug Sources

- Adapters missing proper `async_setup`/`async_teardown` can leak resources
- Registry not updated with all required adapters may cause `AdapterNotFoundError`
- Invalid configs can cause runtime failures

## Logging

All logging uses the centralized `Library.logging` component with structured format and correlation IDs where applicable.

## Usage Example

Create CANBus adapter

config = {"interface": "socketcan", "channel": "can0"}
adapter = await adapter_manager.get_adapter("canbus", config)
List available adapters

adapters = await adapter_manager.list_adapters()