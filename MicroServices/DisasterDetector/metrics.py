from prometheus_client import Counter

DISASTER_DETECTIONS = Counter(
    "disaster_detections_total",
    "Total disasters detected"
)

def record_disaster_detected():
    DISASTER_DETECTIONS.inc()
