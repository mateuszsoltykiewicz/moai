# HAP Component

## Overview

Production-grade HomeKit Accessory Protocol (HAP) integration with security, state synchronization, and monitoring.

## Features

- **HomeKit Integration**: Creates virtual HomeKit accessories
- **State Synchronization**: Syncs component state to HomeKit in real-time
- **mTLS Security**: Enforces mutual TLS for accessory communication
- **Health Monitoring**: Tracks accessory health status
- **Centralized Logging**: Uses `Library.logging` component
- **Metrics**: Tracks operations and accessory status

## API Endpoints

| Endpoint       | Method | Description                  | Security (Required)  |
|----------------|--------|------------------------------|----------------------|
| `/hap/status`  | GET    | Get HAP manager status       | JWT/OIDC, RBAC       |

## Security

- **JWT/OIDC Security**: API endpoints require valid Keycloak-issued JWTs
- **mTLS Enforcement**: All accessory communication uses mutual TLS
- **RBAC**: Requires `hap:read` permission for status endpoint

## Key Components

| File          | Purpose                                                                 |
|---------------|-------------------------------------------------------------------------|
| `manager.py`  | Core HAP accessory management and synchronization                       |
| `api.py`      | FastAPI endpoints with security enforcement                            |
| `schemas.py`  | Pydantic models for configuration and responses                         |
| `metrics.py`  | Prometheus metrics for operations and accessory status                  |

## Usage Example

Initialize HAPManager

hap_manager = HAPManager(
config=hap_config,
component_factory=component_factory,
mtls_manager=mtls_manager
)
await hap_manager.setup()
await hap_manager.start()
Get status

status = await hap_manager.get_status()

## Potential Improvements

- Add support for more accessory types (locks, thermostats)
- Implement accessory removal/update at runtime
- Add persistent state storage for accessories

## Potential Bug Sources

1. **Thread Safety**: Improper synchronization between main thread and HAP thread
2. **Component Compatibility**: Incompatible components may cause state sync failures
3. **mTLS Configuration**: Missing certificates will break accessory communication
4. **State Drift**: Component state changes may not sync to HomeKit

## Security Best Practices

- Rotate mTLS certificates regularly
- Restrict HAP port access to local network
- Validate all component inputs
- Monitor accessory health metrics

## Logging

All operations use `Library.logging` with structured JSON format. Accessory names are logged, but sensitive state data is omitted.
