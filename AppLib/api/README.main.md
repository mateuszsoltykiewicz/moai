# Platform API

This directory contains the main FastAPI application and all API routers for the platform.  
The API is designed for modularity, security, observability, and dynamic configuration.

---

## Features

- **Dynamic router inclusion** based on configuration (with hot reload support)
- **API versioning**: All endpoints are under `/api/v1/`
- **Centralized, standardized error handling**
- **Security headers and CORS** (production-ready)
- **Integrated with secrets and authentication subservices**
- **Ready for observability** (tracing, metrics, logging)
- **Clean startup/shutdown of all background services**

---

## Directory Structure

api/
├── init.py
├── main.py                  # Main FastAPI app (entry point)
├── dependencies.py          # Shared dependencies (auth, pagination, etc.)
└── routers/
├── init.py
├── alarms.py
├── appstate.py
├── audit.py
├── auth.py
├── canbus.py
├── config.py
├── database.py
├── events.py
├── health.py
├── i2c.py
├── kafka.py
├── logging.py
├── metrics.py
├── mtls.py
├── rate_limiting.py
├── secrets.py
├── tracing.py
└── updates.py


---

## How It Works

- Routers are included/excluded at runtime based on the current config (see `AppConfig.routers`).
- Secrets and auth subservices are initialized on startup and available globally via `app.state`.
- Config hot reload: When config changes, routers are re-evaluated and OpenAPI docs are updated automatically.
- Security: All endpoints are protected with best-practice security headers and CORS policies.
- Error handling: Use `APIException` for consistent error responses.

---

## Example: Adding a New Router

1. Create `api/routers/yourfeature.py` with your endpoints.
2. Add to the router mappings in `main.py` (optional or always-included).
3. Update your config schema if you want it to be dynamically enabled/disabled.

---

## Example: Protected Endpoint

from fastapi import APIRouter, Depends
from api.dependencies import get_current_user

router = APIRouter()
async def secure_endpoint(user=Depends(get_current_user)):
  return {“user”: user}


---

## Configuration

- **Routers**: Enable/disable via the `routers` section in your config file.
- **Secrets**: Managed by `/subservices/secrets`, fetched from Vault.
- **Auth**: JWT/OIDC validation via `/subservices/auth`, integrated with Keycloak.

---

## Running the API

uvicorn api.main:app –host 0.0.0.0 –port 8000


Ensure your config, Vault, and Keycloak settings are correct and secrets are available.

---

## Best Practices

- Restrict `allow_origins` in CORS for production.
- Use mTLS for internal endpoints (e.g., `/metrics`).
- Rotate secrets and credentials regularly in Vault.
- Monitor authentication and error logs for security.

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Keycloak Python SDK](https://pypi.org/project/python-keycloak/)
- [HashiCorp Vault](https://www.vaultproject.io/)

---

This API is designed for security, flexibility, and maintainability in modern cloud-native environments.  
For questions or contributions, please see the project documentation or contact the maintainers.
