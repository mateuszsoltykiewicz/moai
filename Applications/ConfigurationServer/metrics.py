from prometheus_client import Counter, Histogram

CONFIG_REQUESTS = Counter(
    "config_server_requests_total",
    "Total config requests",
    ["service", "version", "status"]
)

CONFIG_RELOAD = Counter(
    "config_server_reload_total",
    "Total config reload operations",
    ["service", "status"]
)

def record_config_request(service: str, version: str, status: str = "success"):
    CONFIG_REQUESTS.labels(service=service, version=version, status=status).inc()

def record_config_reload(service: str, status: str = "success"):
    CONFIG_RELOAD.labels(service=service, status=status).inc()
