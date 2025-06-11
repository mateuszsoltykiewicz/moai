# API Dependencies

This module (`api/dependencies.py`) centralizes all reusable FastAPI dependencies for your application.

## Why use dependencies?

- **DRY code:** Avoid repeating authentication, validation, and resource access logic in every endpoint.
- **Maintainability:** Update logic in one place; all endpoints using the dependency benefit.
- **Testability:** Easily mock or override dependencies in tests.
- **Composability:** Chain dependencies for complex logic (e.g., get user, then check role).

## Examples

### 1. Authentication

from fastapi import APIRouter, Depends
from api.dependencies import get_current_user

router = APIRouter()

async def secure_data(user=Depends(get_current_user)):
  return {“data”: “secret”, “user”: user}


### 2. Pagination

from api.dependencies import pagination_params

async def list_items(pagination=Depends(pagination_params)):

# Use pagination‘skip’ and pagination‘limit’
…

### 3. Resource Validation

from api.dependencies import valid_post_id

async def get_post(post=Depends(valid_post_id)):
  return post

### 4. Service/Client Access

from api.dependencies import get_kafka_client

async def produce_message(kafka=Depends(get_kafka_client)):
# Use kafka client here
…


## Best Practices

- **Use `async def` for all dependencies** to ensure non-blocking performance.
- **Document dependencies** with docstrings for clarity and auto-generated docs.
- **Parameterize dependencies** for flexible, reusable logic.
- **Chain dependencies** for composable, layered logic (e.g., get user, then check permissions).

## Extending

- Add new dependencies for:
  - Authorization (role checks)
  - Service access (database, cache, tracing, etc.)
  - Common query parameter parsing
  - Request/response validation
  - Rate limiting, audit logging, etc.

## References

- [FastAPI Dependencies Tutorial](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Advanced Dependencies](https://fastapi.tiangolo.com/advanced/advanced-dependencies/)
- [Structuring a FastAPI Project: Best Practices](https://dev.to/mohammad222pr/structuring-a-fastapi-project-best-practices-53l6)

---

**Centralizing dependencies is key to a robust, maintainable, and scalable FastAPI application.**

