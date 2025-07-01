from prometheus_client import Counter

HOMEKIT_REFRESHES = Counter(
    "homekit_refreshes_total",
    "Total accessory refresh operations"
)

def record_homekit_refresh():
    HOMEKIT_REFRESHES.inc()
