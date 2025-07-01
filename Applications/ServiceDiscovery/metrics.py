from prometheus_client import Counter

DISCOVERY_RUNS = Counter(
    "service_discovery_runs_total",
    "Total number of service discovery runs"
)

UNAUTHORIZED_SERVICE_DETECTIONS = Counter(
    "unauthorized_service_detections_total",
    "Total number of unauthorized services detected"
)
