from prometheus_client import Counter

# Counts successful requests allowed by rate limiting
RATE_LIMIT_ALLOWED = Counter(
    "rate_limit_allowed_total",
    "Total requests allowed by the rate limiter",
    ["scope"]
)

# Counts blocked requests (rate limit exceeded)
RATE_LIMIT_BLOCKED = Counter(
    "rate_limit_blocked_total",
    "Total requests blocked by the rate limiter",
    ["scope"]
)
