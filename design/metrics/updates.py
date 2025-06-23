from prometheus_client import Counter, Histogram
from utils.prometheus_instrumentation import REGISTRY

UPDATES_STARTED = Counter(
    "updates_started_total",
    "Total update attempts",
    registry=REGISTRY
)
UPDATES_COMPLETED = Counter(
    "updates_completed_total",
    "Successful updates",
    registry=REGISTRY
)
UPDATES_FAILED = Counter(
    "updates_failed_total",
    "Failed updates",
    ["phase"],
    registry=REGISTRY
)
UPDATE_DURATION = Histogram(
    "update_duration_seconds",
    "Update process duration",
    registry=REGISTRY
)
UPDATE_RETRIES = Counter(
    "update_retries_total",
    "Update operation retries",
    registry=REGISTRY
)

def record_update_started():
    UPDATES_STARTED.inc()

def record_update_failed(phase: str):
    UPDATES_FAILED.labels(phase=phase).inc()
