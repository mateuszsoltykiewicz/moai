# metrics/updates.py
from prometheus_client import Counter, Histogram

UPDATES_STARTED = Counter("updates_started_total", "Total update attempts")
UPDATES_COMPLETED = Counter("updates_completed_total", "Successful updates")
UPDATES_FAILED = Counter("updates_failed_total", "Failed updates", ["phase"])
UPDATE_DURATION = Histogram("update_duration_seconds", "Update process duration")
UPDATE_RETRIES = Counter("update_retries_total", "Update operation retries")
