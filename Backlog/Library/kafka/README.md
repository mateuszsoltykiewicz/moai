# Kafka Component

## Overview

The Kafka component provides robust, asynchronous producer and consumer management for Apache Kafka within the microservices platform. It supports secure, efficient, and observable message streaming, and enforces JWT/OIDC authentication and RBAC authorization on all API endpoints.

## Features

- **Async Producer & Consumer**: Non-blocking Kafka operations using aiokafka.
- **Dynamic Topic Management**: Easily consume or produce to any topic.
- **JWT/OIDC Security**: All API endpoints require valid Keycloak-issued JWTs and RBAC permissions.
- **Prometheus Metrics**: Tracks operation counts, status, and latency per topic.
- **Centralized Logging**: Uses `Library.logging` for all logs and errors.
- **Error Handling**: Comprehensive error classes and exception chaining.
- **Connection Pooling**: Efficient resource management for high-throughput workloads.

## API Endpoints

| Endpoint                    | Method | Description                       | Security (Required)   |
|-----------------------------|--------|-----------------------------------|-----------------------|
| `/kafka/producer/produce`   | POST   | Produce a message to a topic      | JWT/OIDC, RBAC: write |
| `/kafka/consumer/consume`   | GET    | Consume messages from a topic     | JWT/OIDC, RBAC: read  |

## Requirements

- Kafka cluster (tested with Apache Kafka 2.x+)
- aiokafka Python package
- JWT/OIDC provider (Keycloak recommended)
- Prometheus for metrics scraping

## Usage Example

Producer example

req = KafkaProduceRequest(topic="events", value='{"foo": "bar"}')
await producer_manager.produce(req)
Consumer example

messages = await consumer_manager.consume(topic="events", group_id="service-group", limit=5)
for msg in messages:
print(msg.value)

## Interactions

- **Kafka**: For message transport and streaming.
- **Library.api.security**: JWT/OIDC validation and RBAC enforcement.
- **Library.logging**: For all operational and error logs.
- **Library.metrics**: Prometheus metrics for all Kafka operations.
- **Other Microservices**: For event-driven communication.

## Security

- **JWT/OIDC enforced on all endpoints** using the generic dependency from `Library/api/security.py`.
- **RBAC**: Requires `kafka_producer:write` for producing and `kafka_consumer:read` for consuming.
- **No unauthenticated access** is permitted, including machine-to-machine (M2M) flows.

## Potential Improvements

- Add dead-letter queue support for failed messages.
- Implement consumer lag monitoring and alerting.
- Support for schema registry and message validation.
- Add batch produce/consume endpoints for high-throughput use cases.

## Potential Bug Sources

- **Kafka Connectivity**: Network or broker issues may disrupt message flow.
- **Schema Mismatches**: Payloads must match expected schemas for consumers.
- **Concurrency**: High parallelism may cause lock contention or resource exhaustion.
- **Improper Shutdown**: Not stopping consumers or producers may leak resources.

## Logging

- All operations use `Library.logging` with structured JSON format.
- Errors and exceptions include stack traces (`exc_info=True`).
- Sensitive data is never logged.

## License

Proprietary – Internal use only.

## Last Updated

2025-06-28
