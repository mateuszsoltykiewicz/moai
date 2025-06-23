# AppLib Core Module

## Overview

The `/core` module is the heart of the AppLib platform. It encapsulates all domain logic, business rules, validation, state management, configuration, observability, and essential utilities. This ensures that your business logic is **modular, testable, framework-agnostic, and easy to maintain** as your platform evolves.

---

## Directory Structure

├── init.py
├── config.py         # Async, schema-driven config manager
├── events.py         # Domain events and dispatcher
├── logging.py        # Structured logging (console + Fluentd)
├── models.py         # Domain entities and value objects
├── observability.py  # Unified tracing & metrics setup (OpenTelemetry, Prometheus)
├── services.py       # Business workflows and use cases
├── state.py          # Async, encrypted, versioned state manager
├── tracing.py        # Async distributed tracing integration
├── utils.py          # Core-specific helper functions
├── validators.py     # Business rule validators


---

## Module Responsibilities

| File             | Purpose/Responsibility                                         |
|------------------|---------------------------------------------------------------|
| `models.py`      | Domain entities & value objects (e.g., Device, User)          |
| `services.py`    | Business workflows, orchestrates models & rules               |
| `validators.py`  | Centralized business rule validation                          |
| `events.py`      | Domain events & optional dispatcher for extensibility         |
| `utils.py`       | Pure helper functions for use within core logic               |
| `exceptions.py`  | (In `/exceptions`) Domain-specific error classes              |
| `config.py`      | Async config manager: schema-driven, env overrides, hot reload|
| `state.py`       | Async singleton state: encrypted, versioned, auto-backup      |
| `logging.py`     | Structured logging setup (JSON, console, Fluentd)             |
| `observability.py`| Unified tracing & metrics (OpenTelemetry, Prometheus)        |
| `tracing.py`     | Async tracing context manager (OpenTelemetry/OTLP)            |
| `__init__.py`    | Package docstring and (optionally) public API                 |

---

## Usage Patterns

### 1. Domain Logic Example

from core.models import Device
from core.services import activate_device
from exceptions.core import DeviceAlreadyActiveError

device = Device(device_id=“dev123”, status=“inactive”)
try:
  activate_device(device)
except DeviceAlreadyActiveError:
  print(“Device is already active.”)


### 2. Configuration Management

from core.config import AsyncConfigManager
config_mgr = AsyncConfigManager(“configs/dev/app_config.json”)
await config_mgr.start()
config = await config_mgr.get()


### 3. State Management

from core.state import AppState
state = AppState()
await state.initialize(config)
await state.update_state({“foo”: “bar”}, persist=True)


### 4. Observability & Tracing

from core.observability import Observability
obs = Observability(service_name=“myservice”)
tracer = obs.get_tracer()
meter = obs.get_meter()

from core.tracing import AsyncTracer
tracer = AsyncTracer(“myservice”)
async with tracer.start_span(“important-operation”, {“user_id”: 123}):
await do_async_work()


### 5. Logging

from core.logging import configure_logging
configure_logging(service_name=“myservice”)
import logging logger = logging.getLogger(“app”)
logger.info(“Service started”)


---

## Best Practices

- **Keep all business logic, validation, and state in `/core`—never in adapters or API code.**
- **Use the async config and state managers for all configuration and persistent state.**
- **Centralize logging and observability setup for consistency and maintainability.**
- **Raise and catch domain exceptions from `/exceptions` for all business rule violations.**
- **Document and test all core logic and helpers.**

---

## Extending the Core Module

- Add new domain models, services, or validators as your business logic evolves.
- Extend events and observability for new business or operational requirements.
- Keep `/core` framework-agnostic—no direct database, HTTP, or adapter code.

---

## References

- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Pydantic](https://docs.pydantic.dev/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [Prometheus Python Client](https://github.com/prometheus/client_python)

---

**The `/core` module is your platform’s foundation for scalable, maintainable, and testable business logic. Keep it clean, DRY, and well-documented!**
