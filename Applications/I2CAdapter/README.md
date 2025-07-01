# I2CAdapter

## Overview

Hardware control service for Raspberry Pi Pico integration. Manages power and heating relays with safety-critical operations.

## Features

- **Hardware Control**: PowerCutOff, PowerOn, HeatingStart, HeatingStop commands
- **Safety Protocols**: Automatic shutdown on FATAL alarms
- **Security**: JWT/OIDC + RBAC + mTLS enforcement
- **State Management**: Tracks power/heating state in StateServer
- **Alarm Integration**: Raises FATAL alarms on critical events

## API Endpoints

| Endpoint       | Method | Description           | Security     |
|----------------|--------|-----------------------|--------------|
| `/i2c/command` | POST   | Execute I2C command   | `i2c:write` |

## Hardware Requirements

- Raspberry Pi Pico with I2C/GPIO relays
- Gas valve, spark ignition, and power cut-off relays


## Security

- Hardware commands require `i2c:write` permission
- mTLS enforced for all communications
- Pairing code stored in Vault

## Monitoring

- Prometheus metrics at `/metrics`
- Health checks at `/health/live` and `/health/ready`
- Distributed tracing via OpenTelemetry

## Failure Modes

- **PowerCutOff**: Triggers service shutdown after execution
- **Hardware Failure**: Service exits with code 1 on critical errors
