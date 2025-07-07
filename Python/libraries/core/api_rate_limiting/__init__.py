# /Python/libraries/core/api_rate_limiting/__init__.py
import asyncio
from collections import defaultdict

class AsyncRateLimiter:
    def __init__(self, calls, period):
        self.calls = calls
        self.period = period
        self.timestamps = defaultdict(list)

    async def allow(self, key):
        now = asyncio.get_event_loop().time()
        timestamps = [ts for ts in self.timestamps[key] if now - ts < self.period]
        self.timestamps[key] = timestamps
        if len(timestamps) < self.calls:
            self.timestamps[key].append(now)
            return True
        return False
