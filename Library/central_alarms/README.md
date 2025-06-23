# CentralAlarmsRegistry

## Purpose

CentralAlarmsRegistry provides a centralized, async, and observable registry for alarms and events across all microservices.

## Features

- Async, thread-safe
- API for raising, clearing, querying alarms
- Metrics for all operations
- Suitable for dashboards, alerting, and analytics

## API

- `POST /central_alarms/raise` – Raise or update an alarm
- `POST /central_alarms/clear` – Clear (deactivate) an alarm
- `GET /central_alarms/{id}` – Get alarm by ID
- `GET /central_alarms/` – List all alarms

## Usage

Deploy as a standalone microservice or as part of your platform.
Forward alarms from your local AlarmsManager to this registry.
