# /Python/libraries/core/async_metrics/__init__.py
from prometheus_client import Counter, Gauge, Histogram, start_http_server

def start_metrics_server(port=8000):
    start_http_server(port)

REQUEST_COUNT = Counter('request_count', 'Total requests')
ERROR_COUNT = Counter('error_count', 'Total errors')
LATENCY = Histogram('request_latency_seconds', 'Request latency')
