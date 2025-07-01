from prometheus_client import Counter

SECRETS_ROTATIONS = Counter(
    "secrets_rotator_operations_total",
    "Total secret rotations",
    ["path", "status"]
)

def record_secret_rotation(path: str, status: str = "success"):
    SECRETS_ROTATIONS.labels(path=path, status=status).inc()
