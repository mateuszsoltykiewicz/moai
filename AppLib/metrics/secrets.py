from prometheus_client import Counter
from utils.prometheus_instrumentation import REGISTRY

SECRETS_CREATED = Counter(
    "secrets_created_total",
    "Total number of secrets created",
    ["backend"],
    registry=REGISTRY
)
SECRETS_RETRIEVED = Counter(
    "secrets_retrieved_total",
    "Total number of secrets retrieved",
    ["backend"],
    registry=REGISTRY
)
SECRETS_UPDATED = Counter(
    "secrets_updated_total",
    "Total number of secrets updated",
    ["backend"],
    registry=REGISTRY
)
SECRETS_DELETED = Counter(
    "secrets_deleted_total",
    "Total number of secrets deleted",
    ["backend"],
    registry=REGISTRY
)
SECRETS_ERRORS = Counter(
    "secrets_errors_total",
    "Total number of secret management errors",
    ["backend", "operation"],
    registry=REGISTRY
)

def record_secret_created(backend: str):
    SECRETS_CREATED.labels(backend=backend).inc()

def record_secret_error(backend: str, operation: str):
    SECRETS_ERRORS.labels(backend=backend, operation=operation).inc()
