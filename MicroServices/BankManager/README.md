# BankManager

## Overview

BankManager handles financial transactions and alarm management in the platform. Consumes `sensorData`, produces alarm events, and crashes on FATAL alarms.

## Features

- Processes financial transactions
- Produces to `createAlarm`/`deleteAlarm` topics
- Maintains transaction records
- Stops processing on FATAL alarms
- Integrates with AlarmsServer, StateServer, ConfigurationServer
- Full metrics, tracing, health endpoints
- mTLS and JWT/OIDC security

## API Endpoints

| Endpoint           | Method | Description          | Security (Required)  |
|--------------------|--------|----------------------|----------------------|
| `/bank/transaction`| POST   | Process transaction  | JWT/OIDC, RBAC       |

## Kafka Topics

| Topic          | Direction | Description                |
|----------------|-----------|----------------------------|
| `sensorData`   | Consume   | Input sensor data          |
| `createAlarm`  | Produce   | Alarm creation events      |
| `deleteAlarm`  | Produce   | Alarm resolution events    |

## Security

All endpoints require:

- mTLS client certificates
- Valid JWT with RBAC permissions
- `bank:write` for transaction processing

## Health Checks

- `/health/live`: Liveness
- `/health/ready`: Readiness

## Failure Mode

- **FATAL Alarm**: Immediately crashes service (`sys.exit(1)`)

## Metrics

- `bank_transactions_processed_total`
- `bank_transaction_latency_seconds`

## Last Updated

2025-06-28
