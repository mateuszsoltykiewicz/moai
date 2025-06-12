from prometheus_client import Counter

DB_QUERIES_TOTAL = Counter(
    "db_queries_total", "Total number of database queries", ["operation"]
)
DB_ERRORS_TOTAL = Counter(
    "db_errors_total", "Total database errors", ["operation"]
)
