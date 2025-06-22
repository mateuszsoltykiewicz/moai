import time
from typing import Callable, Dict, Any, Awaitable

class HealthCheckRegistry:
    def __init__(self):
        self._checks = {}

    def register(self, name: str, func: Callable[[], Awaitable[Dict[str, Any]]]):
        self._checks[name] = func

    def get_checks(self):
        return self._checks

health_registry = HealthCheckRegistry()

# Example registration at app startup:
# from api.utils.health import health_registry
# health_registry.register("database", check_database)
# health_registry.register("redis", check_redis)
