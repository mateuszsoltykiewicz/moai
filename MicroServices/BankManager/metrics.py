from prometheus_client import Counter, Histogram

TRANSACTIONS_PROCESSED = Counter(
    "bank_transactions_processed_total",
    "Total transactions processed",
    ["status"]
)

TRANSACTION_LATENCY = Histogram(
    "bank_transaction_latency_seconds",
    "Transaction processing latency",
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

def record_transaction(status: str):
    TRANSACTIONS_PROCESSED.labels(status=status).inc()

def record_transaction_latency(latency: float):
    TRANSACTION_LATENCY.observe(latency)
