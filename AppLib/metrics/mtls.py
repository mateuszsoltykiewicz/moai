from prometheus_client import Counter

MTLS_REQUESTS = Counter(
    "mtls_authenticated_requests_total",
    "Total mTLS-authenticated requests",
    ["client_cn"]
)