from prometheus_client import Counter

HEATING_JOB_OPERATIONS = Counter(
    "heating_job_operations_total",
    "Total heating job operations",
    ["operation"]
)

def record_heating_job_operation(operation: str):
    HEATING_JOB_OPERATIONS.labels(operation=operation).inc()
