# CoreManager

## Purpose

The CoreManager is the central orchestrator for the AppLib platform.  
It coordinates the startup, shutdown, and health of all other managers/components.

## Features

- Async lifecycle management
- Status and health reporting
- Integration with metrics and tracing
- Extensible for orchestration logic

## API

- `GET /core/status` – Returns the current status and state of the CoreManager

## Metrics

- `core_manager_operations_total{operation="setup"}` – Incremented on setup
- `core_manager_operations_total{operation="shutdown"}` – Incremented on shutdown

## Usage

The CoreManager is instantiated and managed at application startup.  
Other managers may register with it for orchestration and coordination.

## Extending

Add orchestration logic, hooks, or additional API endpoints as needed.
