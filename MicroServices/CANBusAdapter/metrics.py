from prometheus_client import Counter

CANBUS_POLLS = Counter(
    "canbus_polls_total",
    "Total CAN bus polls"
)

def record_canbus_poll():
    CANBUS_POLLS.inc()
