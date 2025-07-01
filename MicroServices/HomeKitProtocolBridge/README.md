# HomeKitProtocolBridge

## Overview

HomeKitProtocolBridge exposes your platform's dynamic accessories to Apple HomeKit using the HomeKit Accessory Protocol (HAP). It receives real-time updates from HomeKitBridge via WebSocket and manages HomeKit accessory state accordingly.

## Features

- Native HomeKit protocol via HAP-python
- Dynamic accessory creation and updates
- Real-time integration with backend via WebSocket
- Production-grade error handling and logging

## How it works

1. Connects to HomeKitBridge `/ws/accessories` via WebSocket.
2. Receives JSON updates for all accessories.
3. Dynamically creates/updates HomeKit accessories and characteristics.
4. Exposes them to Apple Home/iOS/Siri.

## Security

- HomeKit pairing, encryption, and authentication handled by HAP-python.
- WebSocket connection can be protected with JWT/mTLS as needed.

## Deployment

- Requires Vault for secure pairing code management.
- Uses environment variables for configuration (e.g., Vault address, WebSocket URL).
- Supports QR code generation for easy pairing.

## Configuration

- `VAULT_ADDR`: Vault server URL
- `VAULT_ROLE_ID`: Vault AppRole ID
- `VAULT_SECRET_ID`: Vault AppRole Secret ID
- `HOMEKIT_BRIDGE_URL`: WebSocket URL to HomeKitBridge
- `HAP_PORT`: Port for HAP server (default 51826)

## Health Checks

- TCP port check on `HAP_PORT`
- WebSocket connectivity check
- Vault secrets accessibility

## Metrics

- WebSocket connection status
- Accessory update latency
- Vault request success rate
- HAP connection count

## Logging

- Structured logging with severity levels
- Logs pairing code and setup ID on startup

## Security Best Practices

- Use Vault AppRole authentication with limited privileges
- Restrict access to Vault secrets
- Use mutual TLS for WebSocket and HAP server
- Rotate pairing codes regularly

## References

- [HAP-python Documentation](https://hap-python-test.readthedocs.io/en/rtdimportfix/api.html)
- [Apple HomeKit Protocol Spec](https://developer.apple.com/homekit/)
- [HomeKit QR Code Generation](https://github.com/SimonGolms/homekit-code)

## Last Updated

2025-07-01
