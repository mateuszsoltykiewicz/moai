# Alarms Component

## Overview

Centralized, async alarm management for microservices. Supports raising, clearing, querying, and notifying on alarm changes, with metrics and centralized logging.

## Features

- **Raise, clear, and query alarms** with unique IDs and metadata
- **Async, thread-safe** operations with asyncio locks
- **Centralized logging** via `Library.logging`
- **Prometheus metrics** for all alarm operations
- **Listener system** for alarm change notifications
- **Integration with central alarm registry** (optional)

## API Endpoints

- `/alarms/raise` (POST): Raise or update an alarm
- `/alarms/clear` (POST): Clear (deactivate) an alarm
- `/alarms/{id}` (GET): Get alarm by ID
- `/alarms/` (GET): List all alarms (optionally filter by active status)

## Interactions

- **CentralAlarmsAdapter**: For forwarding alarms to a central registry
- **Library.logging**: For all logging
- **Library.metrics**: For Prometheus metrics

## Potential Improvements

- Add persistent storage for alarms (currently in-memory)
- Add more granular alarm severity levels and filtering

## Potential Bug Sources

- If central registry is unavailable, alarm forwarding may fail silently
- In-memory alarm storage is not durable (alarms lost on restart)
- Listeners must be robust to exceptions to avoid blocking notifications

## Logging

All logging uses the centralized `Library.logging` component.

## Usage Example

alarms_manager = AlarmsManager()
await alarms_manager.raise_alarm(AlarmRaiseRequest(id="foo", source="sensor", type="fault", details={}))
alarms = await alarms_manager.list_alarms()
