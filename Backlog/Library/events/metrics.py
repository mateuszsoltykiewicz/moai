from prometheus_client import Counter

EVENTS_PUBLISHED = Counter(
    "events_published_total",
    "Total events published by type",
    ["event_type"]
)

EVENTS_CONSUMED = Counter(
    "events_consumed_total",
    "Total events consumed by type",
    ["event_type"]
)

def record_event_published(event_type: str):
    EVENTS_PUBLISHED.labels(event_type=event_type).inc()

def record_event_consumed(event_type: str):
    EVENTS_CONSUMED.labels(event_type=event_type).inc()
