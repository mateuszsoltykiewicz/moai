# CentralStateRegistry

## Overview

**CentralStateRegistry** is a centralized, async, and observable service registry and state aggregator for distributed microservice systems.  
It enables service discovery, cross-service health/status dashboards, and orchestration in Kubernetes or any cloud-native environment.

---

## Key Features

- **Service Registration:** Microservices register their name, version, endpoints, health, and custom metadata.
- **State Updates:** Services can update their status (e.g., healthy, degraded, workload, custom metrics) and send heartbeats.
- **Query API:** Operators and other services can query the registry for the current state of all or selected services.
- **Health/Heartbeat Checks:** Marks services as "stale" if heartbeats are missed.
- **Async & Thread-Safe:** Designed for high concurrency and reliability.
- **Metrics Integration:** All operations are tracked for observability.
- **Kubernetes/Cloud Ready:** Deploy as a standalone microservice or as part of your platform.

---

## API

| Method & Path                | Description                                      |
|------------------------------|--------------------------------------------------|
| `POST /central_state/register` | Register or update a microservice’s state        |
| `GET /central_state/services`  | List all registered services and their states    |
| `GET /central_state/service/{name}` | Get the state of a specific service         |
| `GET /central_state/health`     | Health check for the registry itself            |

---

## Example Usage

### Service Registration (from a microservice)
import httpx
from datetime import datetime

async def register_state():
state = {
  “name”: “orders”,
  “version”: “1.2.0”,
  “status”: “healthy”,
  “endpoints”: {
    “api”: “http://orders:8080/api”},
    “metadata”: {“region”: “eu-west-1”},
    “last_heartbeat”: datetime.utcnow().isoformat()
  }
  
  async with httpx.AsyncClient() as client:
    await client.post(“http://central-state:8000/central_state/register”, json=state)

### Query All Service States (for dashboards)

async with httpx.AsyncClient() as client:
  resp = await client.get(“http://central-state:8000/central_state/services”) 
  print(resp.json())

---

## Deployment

- **Standalone:** Deploy as a FastAPI/Uvicorn service with persistent storage if needed.
- **Kubernetes:** Use a Deployment with multiple replicas for high availability.
- **Security:** Protect API endpoints with mTLS, RBAC, or API keys as needed.
- **Monitoring:** Scrape Prometheus metrics for all operations.

---

## Best Practices

- Each microservice should own its own operational state and database.
- The central registry is for metadata, health, and discovery—not for transactional data.
- Use heartbeats and timeouts to mark services as "stale" or "unhealthy".
- Integrate with dashboards and orchestrators for global visibility.

---

## Example Directory Structure

central_state/
├── manager.py
├── schemas.py
├── api.py
├── exceptions.py
├── metrics.py
└── README.md

---

## Extending

- Add event-driven updates (Kafka, etc.) for distributed state changes if needed.
- Integrate with service mesh or discovery tools for advanced scenarios.
- Add RBAC, audit logging, or notification hooks for production use.

---

## License

[Your License Here]

---

**CentralStateRegistry is the foundation for reliable, observable, and orchestratable microservice platforms.**
