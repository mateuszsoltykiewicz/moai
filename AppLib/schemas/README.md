# AppLib Schemas Module

## Overview

The `schemas` module is the central place for all API and internal data contracts in the AppLib platform. It contains [Pydantic](https://docs.pydantic.dev/) models that define the structure, validation, and documentation for every request and response in the system. These schemas ensure type safety, robust validation, and seamless OpenAPI documentation for all services and adapters in AppLib.

---

## Why Use Schemas?

- **Validation:** All incoming and outgoing data is validated against strict, versioned schemas.
- **Documentation:** FastAPI uses these schemas to generate accurate OpenAPI docs and client SDKs.
- **Maintainability:** Centralized data contracts make it easy to refactor and extend the platform.
- **Security:** Sensitive fields use Pydantic’s `SecretStr`, and schemas are designed to avoid leaking secrets.
- **Interoperability:** Clear, versioned contracts help external clients and microservices interact reliably.

---

## Directory Structure

schemas/
├── init.py\
├── alarms.py
├── audit.py
├── canbus.py
├── config.py├── database.py
├── events.py ├── health.py
├── healthcheck.py ├── i2c.py
├── kafka.py
├── logging.py
├── mtls.py
├── rates.py
├── secrets.py
├── state.py
├── tracing.py
├── updates.py
├── users.py


Each file defines Pydantic models for a specific domain or API surface.

---

## Design Principles

### 1. **Strong Typing**
- All fields use explicit types.
- Enums are used for constrained values (e.g., status, log level).
- `datetime` is used for all timestamps.

### 2. **Extensibility**
- Most schemas include a `details` or `metadata` field for future expansion.
- Where appropriate, schemas include a `version` field for migrations.

### 3. **Validation**
- Field constraints (`ge=1`, `max_length`, regex) prevent invalid data.
- Custom validators are used for cross-field or complex logic.

### 4. **Security**
- Sensitive fields use `SecretStr`.
- Secrets are only returned in secure, authenticated endpoints.

### 5. **Documentation**
- All fields have descriptions.
- OpenAPI examples are provided via `schema_extra` or `model_config`.

---

## File-by-File Summary

| File             | Purpose/Domain                | Example Models                       |
|------------------|------------------------------|--------------------------------------|
| alarms.py        | Alarm/alert events           | `Alarm`, `AlarmLevel`                |
| audit.py         | Audit trail events           | `AuditEvent`, `AuditEventCreate`     |
| canbus.py        | CAN bus config/status        | `CANBusStreamConfigRequest`, `CANBusStatusResponse` |
| config.py        | App config management        | `ConfigResponseSchema`, `ConfigUpdateRequest` |
| database.py      | DB record CRUD               | `DatabaseRecordCreate`, `DatabaseRecordResponse` |
| events.py        | Event/pubsub/webhooks        | `EventPublishRequest`, `WebhookSubscriptionRequest` |
| health.py        | Health check API             | `HealthCheckSchema`                  |
| healthcheck.py   | (Alias of health.py)         | `HealthCheckSchema`                  |
| i2c.py           | I2C hardware API             | `I2CCommandConfigRequest`, `I2CCommandQueueRequest` |
| kafka.py         | Kafka messaging API          | `KafkaProduceRequest`, `KafkaConsumeRequest` |
| logging.py       | Dynamic logging config       | `LogLevelUpdateRequest`, `LoggerStatus` |
| mtls.py          | mTLS status/certificates     | `MTLSStatusResponse`, `CertificateInfo` |
| rates.py         | API rate limiting            | `RateLimitConfigRequest`, `RateLimitStatusResponse` |
| secrets.py       | Secrets management           | `SecretCreateRequest`, `SecretRetrieveResponse` |
| state.py         | App state reporting          | `AppStateSchema`, `AppStateUpdateRequest` |
| tracing.py       | Distributed tracing status   | `TracingStatusResponse`              |
| updates.py       | Update orchestration         | `UpdateCheckResponse`, `UpdateTriggerResponse` |
| users.py         | User management              | `UserSchema`, `UserCreateSchema`     |

---

## Usage Examples

### 1. **Request Validation**

from schemas.users import UserCreateSchema
def create_user(data: dict):
  user = UserCreateSchema.parse_obj(data)


### 2. **OpenAPI Documentation**

- FastAPI automatically uses these schemas for OpenAPI docs.
- Field descriptions and examples appear in the interactive docs.

### 3. **Extending Schemas**

- Add new fields or Enums as your platform evolves.
- Use inheritance for shared fields across related schemas.

---

## Best Practices

- **Keep schemas in sync** with your models and API endpoints as you add new features.
- **Consolidate duplicates:** If two files (e.g., `health.py` and `healthcheck.py`) serve the same purpose, merge them.
- **Automate JSON Schema export** if you need to provide schemas to external consumers.
- **Write or update tests** for schema validation, especially for edge cases and custom validators.

---

## FAQ

### Q: Why not use JSON Schema files (`validation/`) anymore?
A: Pydantic models generate JSON Schema automatically, and FastAPI uses these for validation and docs. Maintaining separate JSON files risks drift and is redundant unless you have non-Python consumers.

### Q: How do I generate JSON Schema from a Pydantic model?
A: Use `.model_json_schema()` or `schema_of()` to export the schema for any model.

---

## Adding a New Schema

1. Create a new file (e.g., `schemas/telemetry.py`).
2. Define your Pydantic models, using Enums and field constraints as needed.
3. Add field descriptions and OpenAPI examples.
4. Import and use the schema in your routers or services.

---

## References

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [JSON Schema Generation in Pydantic](https://docs.pydantic.dev/latest/concepts/models/#json-schema-generation)
- [OpenAPI Specification](https://swagger.io/specification/)

---

**Your `schemas` module is production-grade, extensible, and well-documented.  
It is the foundation for robust, maintainable, and secure APIs in AppLib.**
