"""
Enhanced metrics for mTLS operations.
"""

from prometheus_client import Counter, Histogram

MTLS_OPERATIONS = Counter(
    "mtls_operations_total",
    "Total mTLS operations",
    ["operation", "status"]
)

MTLS_CERT_EXPIRY = Histogram(
    "mtls_cert_expiry_days",
    "Days until certificate expiration",
    ["cert_type"]
)

def record_mtls_operation(operation: str, status: str = "success"):
    MTLS_OPERATIONS.labels(operation=operation, status=status).inc()

def record_cert_expiry(cert_type: str, days_remaining: float):
    MTLS_CERT_EXPIRY.labels(cert_type=cert_type).observe(days_remaining)
