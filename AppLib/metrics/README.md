## Metrics Module (`/metrics`)

All Prometheus metrics are defined in the `/metrics` package, organized by subservice, adapter, or router.

**Structure:**
- `metrics/adapters.py` — Metrics for hardware adapters (CANBus, I2C, etc.)
- `metrics/database.py` — Metrics for database operations
- `metrics/kafka.py` — Metrics for Kafka producer/consumer
- `metrics/app.py` — General app-level metrics (uptime, version, etc.)

**Usage:**
- Import and increment/update metrics in your routers, adapters, and subservices.
- Expose metrics via `/metrics` (Prometheus scraping) and/or `/api/v1/metrics/custom` (internal dashboards).

**Best Practices:**
- Use labels (e.g., `adapter_id`, `topic`, `operation`) for high-cardinality metrics.
- Update metrics in business logic and error handlers.
- Keep metric definitions organized by domain for maintainability.

## Rate Limiting Metrics

**rate_limit_allowed_total{scope="user"}**  
Total requests allowed by the rate limiter for the given scope.

**rate_limit_blocked_total{scope="user"}**  
Total requests blocked (rate limit exceeded) for the given scope.

**Best Practices:**
- Use these metrics to monitor abuse, tune limits, and alert on excessive blocking.
- Add more labels (e.g., endpoint, user role) if you need higher granularity.
