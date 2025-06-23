# AlarmsManager

## Overview

**AlarmsManager** provides async, thread-safe, and observable alarm management for each microservice or application instance.  
It is designed to work both as a local alarms/event store and as a forwarder to a centralized alarms registry, enabling robust, scalable, and unified alarm management across your distributed system.

---

## Key Features

- **Async, Thread-Safe:** All operations are async and safe for concurrent use.
- **Local Alarm Storage:** Raise, clear, and query alarms within the microservice.
- **Listener Registration:** Register async listeners for alarm changes (for in-app reactions).
- **API:** Exposes endpoints for raising, clearing, and listing alarms.
- **Metrics:** Prometheus integration for all alarm operations.
- **Centralized Forwarding:** Optionally forwards all alarm events to a CentralAlarmsRegistry for unified, cross-service visibility and analytics.

---

## CentralAlarmsRegistry Integration

- **Purpose:**  
  The CentralAlarmsRegistry is a standalone service (or component) that aggregates alarms from all microservices, enabling unified dashboards, analytics, and alerting.

- **How It Works:**  
  - Each AlarmsManager instance can be configured with a CentralAlarmsAdapter.
  - When an alarm is raised or cleared locally, it is also forwarded to the CentralAlarmsRegistry via HTTP API (or Kafka/event bus if preferred).
  - The central registry provides APIs for querying, analytics, and policy management across the entire system.

- **Benefits:**  
  - Local autonomy for immediate actions and resilience.
  - Global visibility and control for operations, compliance, and analytics.

---

## API

| Method & Path         | Description                       |
|-----------------------|-----------------------------------|
| `POST /alarms/raise`  | Raise or update a local alarm     |
| `POST /alarms/clear`  | Clear (deactivate) a local alarm  |
| `GET /alarms/{id}`    | Get alarm by ID                   |
| `GET /alarms/`        | List all local alarms             |

**CentralAlarmsRegistry API (see its README for details):**
- `POST /central_alarms/raise`
- `POST /central_alarms/clear`
- `GET /central_alarms/`
- `GET /central_alarms/{id}`

---

## Example: Forwarding to Central Registry

from alarms.central_registry_adapter import CentralAlarmsAdapter

alarms_manager = AlarmsManager(central_registry_url=“http://central-alarms:8000”)

When raising or clearing an alarm:
await alarms_manager.raise_alarm(alarm_req)  # This also forwards to central registry if configured

---

## Example Directory Structure

alarms/
├── manager.py
├── schemas.py
├── api.py
├── exceptions.py
├── metrics.py
├── central_registry_adapter.py
└── README.md

---

## Best Practices

- Always forward alarms to the CentralAlarmsRegistry for unified visibility and compliance.
- Use local listeners for immediate, in-app reactions (e.g., circuit breakers, local UI).
- Integrate dashboards and alerting systems with the central registry for cross-service analytics.
- Secure both local and central alarm APIs with authentication and RBAC.
- Monitor alarm rates and types with Prometheus metrics.

---

## Extending

- Add Kafka or other event bus adapters for high-scale, multi-region deployments.
- Implement alarm policy sync: pull policies from the central registry to enforce consistent thresholds/escalation.
- Add notification hooks (email, Slack, PagerDuty) to the central registry for critical alarms.

---

## License

[Your License Here]

---

**AlarmsManager + CentralAlarmsRegistry = robust, scalable, and observable alarm management for the cloud-native era.**
