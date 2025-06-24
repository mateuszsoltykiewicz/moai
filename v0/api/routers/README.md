
## Alarms API (`alarms.py`)

This router provides endpoints to create and query system alarms.

**Endpoints:**
- `GET /api/v1/alarms/` — List all alarms (optionally filter by level)
- `POST /api/v1/alarms/` — Create a new alarm (requires schema-compliant payload)
- `GET /api/v1/alarms/{code}` — Get a specific alarm by code

**Authentication:**  
All endpoints require a valid access token.

**Schema Example:**

{
  “code”: “DATABASE_CONNECTION_LOST”,
  “message”: “Database connection lost for more than 5 seconds.”,
  “level”: “critical”,
  “timestamp”: “2025-06-11T17:15:00Z”,
  “details”: {“host”: “db1”, “retry_count”: 3}
}

## App State API (`appstate.py`)

This router provides endpoints to query and update the operational state of the application.

**Endpoints:**
- `GET /api/v1/appstate/` — Get current app state (status, uptime, version)
- `POST /api/v1/appstate/` — Update app state (e.g., to "maintenance" or "paused")

**Authentication:**  
All endpoints require a valid access token.

**Schema Example:**

{
  “status”: “maintenance”,
  “uptime_seconds”: 12345,
  “version”: “1.0.0”,
  “details”: {“last_reason”: “Scheduled update”}
}

## Audit API (`audit.py`)

This router provides endpoints to log and query audit events for security and compliance.

**Endpoints:**
- `GET /api/v1/audit/` — List audit events (filter by user/action, with limit)
- `POST /api/v1/audit/` — Log a new audit event (requires schema-compliant payload)
- `GET /api/v1/audit/{event_id}` — Get a specific audit event by ID

**Authentication:**  
All endpoints require a valid access token.

**Schema Example:**

{
  “id”: “uuid-string”,
  “user”: “alice”,
  “action”: “update_config”,
  “resource”: “config.yaml”,
  “timestamp”: “2025-06-12T10:00:00Z”,
  “details”: {“ip”: “1.2.3.4”}
}

## CANBus API (`canbus.py`)

This router provides endpoints to configure and monitor CANBus streaming adapters, such as those based on Raspberry Pi Pico.

**Endpoints:**
- `POST /api/v1/canbus/stream/configure` — Configure an adapter for CANBus streaming
- `GET /api/v1/canbus/status/{adapter_id}` — Get the current status of a CANBus adapter

**Authentication:**  
All endpoints require a valid access token.

**Schema Example:**

{
  “adapter_id”: “can0”,
  “bitrate”: 500000,
  “filters”: {“id”: 123, “mask”: 255}
}

## CANBus API (`canbus.py`)

This router provides endpoints to configure, monitor, and stream data from CANBus adapters (e.g., Raspberry Pi Pico, CANPico).

**Endpoints:**
- `POST /api/v1/canbus/stream/configure` — Configure an adapter for CANBus streaming (real hardware)
- `GET /api/v1/canbus/status/{adapter_id}` — Get the current status of a CANBus adapter
- `GET /api/v1/canbus/stream/{adapter_id}` — Stream CANBus messages (returns up to `max_messages`)

**Authentication:**  
All endpoints require a valid access token.

## Config API (`config.py`)

This router provides endpoints to securely retrieve and update the application configuration.

**Endpoints:**
- `GET /api/v1/config/` — Get the current configuration
- `POST /api/v1/config/` — Update the configuration (triggers hot reload)

**Authentication:**  
All endpoints require a valid access token.  
(Optionally, restrict updates to admin roles.)

**Schema Example:**

{
  “config”: {
    “routers”: {
      “canbus”: true,
      “database”: false,
      …
      },
        “auth”: {“enabled”: true},
        …
      },
      “reason”: “Routine update”
}

## Database API (`database.py`)

**Endpoints:**
- `POST /api/v1/database/` - Create record
- `GET /api/v1/database/` - List all records
- `GET /api/v1/database/{id}` - Get specific record
- `DELETE /api/v1/database/{id}` - Delete record

**Features:**
- Full async SQLAlchemy integration
- UUID primary keys
- JSON data storage
- Production-grade error handling
- Session-per-request pattern

**Authentication:**  
All endpoints require valid JWT token.

**Production Setup:**
1. Configure database URL in your config service
2. Run migrations to create `records` table
3. Add indexes/constraints as needed

## Events API (`events.py`)

This router provides endpoints to publish/query events, register webhooks, and subscribe to event topics.

**Endpoints:**
- `POST /api/v1/events/publish` — Publish an event (triggers webhooks)
- `GET /api/v1/events/list?topic=...` — List recent events (with filtering)
- `POST /api/v1/events/webhook/subscribe` — Register a webhook for a topic (with optional filter)
- `POST /api/v1/events/webhook` — Example webhook endpoint (for testing)

**Webhook Subscription Example:**
{
  “topic”: “sensor-updates”,
  “url”: “https://yourapp.com/webhooks/sensor”,
  “filter”: {“device_id”: “abc123”}
}

**Filtering:**
- Use query parameters like `key=...` or `value_filter={"field":"value"}` (as JSON) on `/list` to filter events.

## Health API (`health.py`)

This router provides endpoints for liveness, readiness, and Prometheus metrics.

**Endpoints:**
- `GET /api/v1/health/livez` — Liveness probe (is the process up)
- `GET /api/v1/health/readyz` — Readiness probe (are all dependencies healthy)

**Liveness:**  
- Returns 200 if the process is running.
- Used by Kubernetes/docker to restart unhealthy containers.

**Readiness Checks:**
1. **Database**: Connection and basic query
2. **Kafka**: Producer/consumer connectivity
3. **I2C**: Adapter health checks
4. **mTLS**: Client certificate presence (via proxy headers)

**Prometheus Metrics:**  
- `/metrics` is exposed using `prometheus_fastapi_instrumentator`.
- Add custom metrics as needed (see [Instrumentator docs](https://github.com/trallnag/prometheus-fastapi-instrumentator)).

## I2C API (`i2c.py`)

This router provides endpoints to configure GPIO pins and queue commands for I2C adapters (e.g., Raspberry Pi Pico).

**Endpoints:**
- `POST /api/v1/i2c/command/configure` — Configure a GPIO pin for an I2C adapter
- `POST /api/v1/i2c/command/queue` — Queue commands for an I2C adapter

**Authentication:**  
All endpoints require a valid access token.

## Kafka API (`kafka.py`)

This router provides advanced endpoints for Kafka:

- Produce and consume with manual/auto offset commit
- Offset reset and replay support
- Topic creation and configuration
- WebSocket streaming for real-time data

**Endpoints:**
- `POST /api/v1/kafka/produce` — Produce a message
- `POST /api/v1/kafka/consume` — Advanced consume (manual/auto commit, offset, partition)
- `POST /api/v1/kafka/topic/create` — Create a topic with advanced config
- `POST /api/v1/kafka/topic/configure` — Update topic config
- `WS /api/v1/kafka/stream/{topic}` — Real-time streaming via WebSocket

## Logging API (`logging.py`)

This router provides endpoints to view and update log levels at runtime.

**Endpoints:**
- `GET /api/v1/logging/` — List all loggers and their levels
- `POST /api/v1/logging/level` — Update the log level for a logger

**Logging Integration:**
- All logs are sent to both the console and Fluentd as structured JSON.
- Fluentd can forward logs to ELK, Loki, Better Stack, or any other backend.
- Use `/api/v1/logging/level` to change log levels dynamically for debugging or incident response.

## Metrics API (`metrics.py`)

This router provides endpoints for custom application and hardware metrics.

**Endpoints:**
- `GET /metrics` — Prometheus metrics endpoint (auto-instrumented, no auth, for Prometheus scraping)
- `GET /api/v1/metrics/custom` — Custom metrics for internal dashboards (requires authentication)

**Custom Metrics Examples:**
- `i2c_commands_total{adapter_id="i2c-1"}`
- `canbus_errors_total{adapter_id="can0"}`
- `db_queries_total{operation="insert"}`
- `kafka_messages_produced_total{topic="events"}`
- `app_uptime_seconds`

**Best Practices:**
- Use `/metrics` for Prometheus/Grafana integration.
- Use `/api/v1/metrics/custom` for internal dashboards with access control.
- Add and update metrics in your business logic and error handlers.

## mTLS API

**Key Components:**
- **Proxy Enforcement**: mTLS is enforced at the ingress (nginx/envoy) level
- **Health Check**: `/readyz` verifies client cert header presence
- **Cert Management**: cert-manager issues server/client certs and manages CA

**Endpoints:**
- `GET /api/v1/mtls/status` — Check if request used mTLS
- `GET /api/v1/mtls/secure` — Example mTLS-protected endpoint

## Rate Limiting API (`rate_limiting.py`)

This router provides endpoints to configure and check rate limiting, and a dependency for per-user/IP/global rate limiting.

**Endpoints:**
- `GET /api/v1/rate_limiting/config/{scope}` — Get rate limit config
- `POST /api/v1/rate_limiting/config` — Set rate limit config
- `GET /api/v1/rate_limiting/status/{scope}` — Get current rate limit status

**Usage:**
- Use `rate_limit_dependency` as a dependency in any endpoint to enforce rate limits.

## Secrets API (`secrets.py`)

This router provides endpoints to securely store, retrieve, update, and delete secrets.

**Endpoints:**
- `POST /api/v1/secrets/` — Create a new secret
- `GET /api/v1/secrets/{name}` — Retrieve a secret by name
- `PUT /api/v1/secrets/{name}` — Update a secret by name
- `DELETE /api/v1/secrets/{name}` — Delete a secret by name

**Authentication:**  
All endpoints require a valid access token.

## Secrets API with Vault Integration

This router provides endpoints to securely store, retrieve, update, and delete secrets using HashiCorp Vault.

**Endpoints:**
- `POST /api/v1/secrets/` — Create a new secret
- `GET /api/v1/secrets/{name}` — Retrieve a secret by name
- `PUT /api/v1/secrets/{name}` — Update a secret by name
- `DELETE /api/v1/secrets/{name}` — Delete a secret by name

## Tracing API (`tracing.py`)

This router provides endpoints to check tracing status and create custom trace spans.

**Endpoints:**
- `GET /api/v1/tracing/status` — Check tracing status and exporter info
- `GET /api/v1/tracing/demo-span` — Create a custom span (for troubleshooting/demo)

**Production Note:**
- Tracing is enabled via OpenTelemetry and exported to Jaeger/Zipkin/OTLP.
- All requests are automatically traced; use custom spans for advanced observability.
- Secure trace data and restrict access to tracing endpoints in production.

- Uses `/adapters/vault.py` for all Vault interactions.
- Vault connection and token are managed via environment variables or Kubernetes secrets.
- Use Vault policies for fine-grained access control and enable audit logging.

- Replace the in-memory store with a secure backend (e.g., Vault, AWS Secrets Manager, encrypted DB).
- Enforce RBAC to restrict who can access or modify secrets.
- Audit all access and changes for compliance.
- Never log secret values.

- Use Redis or another distributed store for rate limit counters.
- Tune limits and periods to match your business requirements.
- Consider advanced patterns (sliding window, leaky bucket) for more precise control.

- Client cert info is passed via `X-Client-Cert` header (configured in ingress)
- Use cert-manager `Certificate` resources for automated cert rotation

- Use environment variables to configure Fluentd host/port.
- Restrict access to log level changes via RBAC.
- For sensitive environments, mask secrets in logs and use TLS for Fluentd connections.

- Supports manual and auto offset commit
- Supports offset reset (`earliest`, `latest`)
- Supports topic config and partitioning
- WebSocket endpoint for live dashboards and monitoring

- Uses `aiokafka` for async Kafka integration.
- Configure Kafka settings via your config service.
- For production, consider partitioning, retention, and consumer group strategies.
- Add observability and error logging as needed.

- Integrates with `I2CAdapter` in `/subservices/adapters/i2c.py`.
- Replace the in-memory adapter registry with a robust lifecycle manager for real deployments.
- Add observability, error logging, and hardware health checks as needed.
 
- Extend subsystem checks as needed for your stack.
- Configure `/livez` and `/readyz` as liveness/readiness probes in your deployment.
 
Replace the in-memory `AUDIT_EVENTS` list with a persistent database or audit microservice integration.
 
Replace the in-memory `ALARMS` list with a persistent database or alarms microservice integration.

Replace the in-memory state with a persistent store or service for distributed deployments.  
Add RBAC or admin-only restrictions to the update endpoint if needed.

Replace the in-memory `CANBUS_ADAPTERS` dict with integration to your actual CANBus adapter or microservice.

- Uses `python-can` for real CAN hardware integration.
- For MicroPython/CircuitPython (e.g., CANPico), use a serial or USB bridge and adapt the `CANBusAdapter` class accordingly.
- Replace the in-memory adapter registry with a persistent or distributed registry for multi-instance deployments.

- Integrates with the async config subservice for hot reload and validation.
- Audit all config changes for compliance and troubleshooting.
- Filter sensitive fields before returning config in production if needed.

- Uses SQLAlchemy async ORM and Pydantic schemas.
- Update `DATABASE_URL` in `db/session.py` for your environment.
- Extend the schema/model for your real data structure.

- Use a persistent store for `WEBHOOK_REGISTRY` (e.g., database, Redis) in production.
- Add signature validation and retry logic for webhook delivery.
- Integrate with your event streaming backend (Kafka, NATS, etc.) via `/sessions/kafka.py`.

- Extend the subsystem checks for your actual infrastructure (database, Kafka, adapters, etc.).
- Integrate with your app’s startup to set `app.state.version` and other stateful info.
- Use this endpoint for Kubernetes liveness/readiness probes and external monitoring.

- mTLS check validates that client cert info is being passed by the proxy
- Actual cert validation happens at the proxy/ingress layer



