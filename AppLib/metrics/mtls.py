from prometheus_client import Counter
from utils.prometheus_instrumentation import REGISTRY

MTLS_REQUESTS = Counter(
    "mtls_authenticated_requests_total",
    "Total mTLS-authenticated requests",
    ["client_cn"],
    registry=REGISTRY
)

def record_mtls_request(client_cn: str):
    MTLS_REQUESTS.labels(client_cn=client_cn).inc()
