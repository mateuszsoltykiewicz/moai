# AppLib Metrics Module

## Overview

The `metrics` module defines, documents, and manages all Prometheus metrics for the AppLib platform. Each file in this module corresponds to a specific domain (e.g., Kafka, database, adapters, mTLS, rate limiting, secrets, HTTP, tracing, updates) and contains production-ready metric definitions and update helpers.

All metrics are registered to a shared registry (`REGISTRY`) from [`/utils/prometheus_instrumentation.py`](../utils/prometheus_instrumentation.py), ensuring consistency, testability, and compatibility with multiprocess setups.

---

## Why Use This Module?

- **Centralization:** All metrics are defined in one place, making it easy to audit, extend, and maintain observability standards.
- **Consistency:** Naming conventions, label usage, and helper functions are standardized across all domains.
- **Separation of Concerns:** Adapters and services import metrics and helpers from this module, keeping business logic clean.
- **Testability:** Metrics and helpers can be easily mocked or tested in isolation.
- **Extensibility:** New domains or metrics can be added by following the established pattern.

---

## Directory Structure

metrics/
├── README.md
├── adapters.py
├── database.py
├── kafka.py
├── mtls.py
├── rate_limiting.py
├── secrets.py
├── sessions.py
├── tracing.py
└── updates.py


---

## Usage Pattern

1. **Define all metrics and helpers in `/metrics/<domain>.py`.**
2. **Import and use helpers in adapters, routers, or services.**
3. **Expose metrics using the `/utils/prometheus_instrumentation.py` registry via your `/metrics` endpoint.**

---

## Metrics Reference Table

| File              | Example Metrics                       | Labels                        | Helper Functions                |
|-------------------|---------------------------------------|-------------------------------|----------------------------------|
| `kafka.py`        | Messages produced/consumed, errors    | `topic`, `error_type`         | `record_kafka_produced`, ...     |
| `database.py`     | Queries, errors                       | `operation`                   | `record_db_query`, ...           |
| `adapters.py`     | I2C/CAN commands, errors              | `adapter_id`                  | `record_i2c_command`, ...        |
| `mtls.py`         | Authenticated requests                | `client_cn`                   | `record_mtls_request`            |
| `rate_limiting.py`| Allowed/blocked requests              | `scope`                       | `record_rate_limit_allowed`, ... |
| `secrets.py`      | CRUD ops, errors                      | `backend`, `operation`        | `record_secret_created`, ...     |
| `sessions.py`     | HTTP/system metrics                   | `method`, `endpoint`, ...     | `record_http_request`, ...       |
| `tracing.py`      | Traces, spans, errors                 | *(see file)*                  | `observe_span_duration`          |
| `updates.py`      | Update lifecycle                      | `phase`                       | `record_update_started`, ...     |

---

## Example: Kafka Metrics

metrics/kafka.py
from prometheus_client import Counter, Histogram
from utils.prometheus_instrumentation import REGISTRY
KAFKA_MESSAGES_PRODUCED = Counter(
  “kafka_messages_produced_total”,
  “Total Kafka messages produced”,
  “topic”,
  registry=REGISTRY
  )
def record_kafka_produced(topic: str):
  KAFKA_MESSAGES_PRODUCED.labels(topic=topic).inc()


**Usage in an adapter:**

from metrics.kafka import record_kafka_produced
def produce_message(topic, message):# … produce logic … record_kafka_produced(topic)


---

## Adding a New Metric

1. **Open or create the appropriate domain file in `/metrics`.**
2. **Define the metric using the shared `REGISTRY`.**
3. **Add a helper function for updating the metric, enforcing label consistency.**
4. **Document the metric and its labels with a docstring or comment.**
5. **Import and use the helper in your adapters or services.**

---

## Best Practices

- **All metrics must use the shared `REGISTRY` from `/utils/prometheus_instrumentation.py`.**
- **Avoid high-cardinality labels (e.g., user IDs, full URLs).**
- **Document each metric and label for clarity and onboarding.**
- **Write tests for helpers and ensure metrics increment/observe as expected.**
- **Expose metrics via a `/metrics` endpoint using the shared registry.**

---

## Exposing Metrics

To expose metrics for Prometheus scraping, use the shared registry in your FastAPI/Flask app:

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from utils.prometheus_instrumentation import REGISTRY
from fastapi import FastAPI, Response
app = FastAPI()
async def metrics():
  data = generate_latest(REGISTRY)
  return Response(content=data, media_type=CONTENT_TYPE_LATEST)


---

## References

- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Prometheus Metric Naming](https://prometheus.io/docs/practices/naming/)
- [Prometheus Label Best Practices](https://prometheus.io/docs/practices/instrumentation/#use-labels-judiciously)

---

**The `metrics` module is your single source of truth for all platform observability.  
Keep it organized, documented, and DRY for scalable, production-grade monitoring.**
