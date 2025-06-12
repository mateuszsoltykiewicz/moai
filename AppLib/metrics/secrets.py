from prometheus_client import Counter

SECRETS_CREATED = Counter(
    "secrets_created_total",
    "Total number of secrets created",
    ["backend"]
)
SECRETS_RETRIEVED = Counter(
    "secrets_retrieved_total",
    "Total number of secrets retrieved",
    ["backend"]
)
SECRETS_UPDATED = Counter(
    "secrets_updated_total",
    "Total number of secrets updated",
    ["backend"]
)
SECRETS_DELETED = Counter(
    "secrets_deleted_total",
    "Total number of secrets deleted",
    ["backend"]
)
SECRETS_ERRORS = Counter(
    "secrets_errors_total",
    "Total number of secret management errors",
    ["backend", "operation"]
)
