# Events Component

## Overview

Central event bus for asynchronous communication between microservices. Provides schema validation, metrics, and reliable delivery using Kafka.

## Features

- **Schema Validation**: All events validated against Pydantic models
- **Kafka Integration**: Uses Kafka for reliable event delivery
- **Metrics Integration**: Tracks events published and consumed
- **Centralized Logging**: Uses `Library.logging` component
- **Error Handling**: Comprehensive error logging and dead-letter support

## Key Components

| Component         | Purpose                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `EventBus`        | Core class for publishing/consuming events                              |
| `event_registry`  | Central registry of event types and schemas                             |
| `metrics.py`      | Prometheus metrics for event operations                                 |
| `exceptions.py`   | Custom errors for event validation and bus operations                   |

## Usage

### Publishing Events

await event_bus.publish("AlarmRaised", {
"id": "alarm-001",
"source": "sensor",
"type": "temperature_high",
"details": {"value": 42.5},
"timestamp": "2025-06-28T12:34:56Z"
})

### Consuming Events

async def handle_alarm(event: AlarmRaisedEvent):
logger.info(f"Handling alarm: {event.id}")
await event_bus.consume("AlarmRaised", handle_alarm, group_id="alarm-handlers")

## Event Types
The registry includes 17+ event types across categories:
- Alarms
- Service State
- Sensor Data
- Configuration
- Jobs
- Audit
- Accessories

## Interactions

- **Kafka**: For event transport
- **Library.logging**: Centralized logging for all operations
- **All Microservices**: Produce and consume events
- **Library.metrics**: Operation metrics collection

## Potential Improvements

- Add dead-letter queue support for failed messages
- Implement event versioning for schema evolution
- Add schema registry integration

## Potential Bug Sources

1. **Schema Mismatches**: Event payloads must match registered schemas
2. **Kafka Connectivity**: Network issues may disrupt event delivery
3. **Consumer Lag**: Slow consumers may cause message backlog
4. **Serialization Errors**: Invalid JSON payloads break consumers

## Security Best Practices

- Validate all event payloads against schemas
- Use encrypted connections to Kafka
- Implement proper ACLs for Kafka topics
- Rotate Kafka credentials regularly

## Logging

All operations use `Library.logging` with structured JSON format. Event payloads are logged only at debug level.
