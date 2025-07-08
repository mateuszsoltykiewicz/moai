# CANBus Component

## Overview

Production-grade CAN bus manager for hardware integration. Provides async message streaming, sensor configuration, and error recovery for CAN bus interfaces.

## Features

- **Async Message Handling**: Producer/consumer architecture with buffering
- **Sensor Configuration**: Per-sensor arbitration ID and type mapping
- **Error Recovery**: Automatic retries on read failures
- **Metrics Integration**: Tracks messages and operations
- **Centralized Logging**: Uses `Library.logging` component

## API Endpoints

| Endpoint         | Method | Description                          | Response Model               |
|------------------|--------|--------------------------------------|------------------------------|
| `/canbus/stream` | GET    | Stream messages for a sensor         | `List[CanbusStreamResponse]` |
| `/canbus/sensors`| GET    | List configured sensors              | `List[str]`                  |

## Key Components

| File              | Purpose                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `manager.py`      | Core CAN bus management and message processing                          |
| `api.py`          | FastAPI endpoints for streaming and sensor listing                      |
| `schemas.py`      | Pydantic models for configuration and responses                         |
| `metrics.py`      | Prometheus metrics for operations and message counts                    |
| `exceptions.py`   | Custom errors for CAN bus operations                                    |

## Interactions

- **Library.logging**: Centralized logging for all operations
- **Library.metrics**: Operation and message metrics
- **Hardware**: Interfaces with physical CAN bus devices
- **StateServer**: Can forward processed sensor data

## Potential Improvements

- Add message decoding/encoding for different sensor types
- Implement persistent message storage for historical data
- Add health checks and interface monitoring

## Potential Bug Sources

1. **Hardware Dependencies**: Missing `python-can` package or drivers
2. **Queue Overflows**: High message rates may cause dropped messages
3. **Clock Drift**: Timestamp inaccuracies without hardware sync
4. **Sensor Mismatches**: Incorrect arbitration IDs cause missed messages

## Logging

All operations use `Library.logging` with structured JSON format. Debug logs show message details, errors include stack traces.

## Usage Example

config = {
"interface": "can0",
"baudrate": 500000,
"sensors": [
{"name": "engine_temp", "arbitration_id": 0x7E8, "type": "temperature"}
]
}
canbus_manager = CanbusManager(config)
await canbus_manager.setup()
Get latest engine temperature readings

readings = await canbus_manager.stream_sensor("engine_temp", limit=5)


## Security Considerations

- Restrict physical access to CAN bus interfaces
- Validate all configuration inputs to prevent injection
- Use message authentication where supported by hardware
