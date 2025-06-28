# I2C Component

## Overview

Production-grade I2C hardware manager with async control, status monitoring, and error handling.

## Features

- **Async Control**: Thread-safe device control with validation
- **Status Monitoring**: Device status and value retrieval
- **Watchdog**: Periodic device health checks
- **Centralized Logging**: Uses `Library.logging` component
- **Prometheus Metrics**: Tracks operations and durations
- **JWT/OIDC Security**: All API endpoints require authentication and authorization

## API Endpoints

| Endpoint       | Method | Description                  | Security (Required)  |
|----------------|--------|------------------------------|----------------------|
| `/i2c/control` | POST   | Control a device (on/off)    | JWT/OIDC, RBAC       |
| `/i2c/status`  | GET    | Get device status            | JWT/OIDC, RBAC       |
| `/i2c/devices` | GET    | List all devices             | JWT/OIDC, RBAC       |

## Interactions

- **Hardware**: Controls I2C devices and GPIO relays
- **Library.logging**: Centralized logging
- **Library.metrics**: Prometheus metrics
- **Library.api.security**: JWT/OIDC and RBAC enforcement

## Potential Improvements

- Add support for more device types
- Implement persistent device state storage
- Add detailed error recovery and alerts

## Potential Bug Sources

1. **Hardware Dependencies**: Missing `smbus2` or `gpiozero` packages
2. **Device State Mismatch**: Relay state may desync with actual hardware
3. **Concurrency Issues**: Improper locking may cause race conditions
4. **Error Handling**: Unhandled exceptions in hardware control

## Logging

All operations use `Library.logging` with structured JSON format. Errors include stack traces.

## Usage Example

config = {
"bus": 1,
"devices": [
{"name": "sensor1", "address": 32, "type": "temperature"}
],
"gpio_pins": {
"relay1": 17
}
}
i2c_manager = I2CManager(config)
await i2c_manager.setup()
Control device

await i2c_manager.control(I2CControlRequest(device="relay1", action="on"))
Get status

status = await i2c_manager.get_status("sensor1")