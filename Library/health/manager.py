"""
HealthManager: Centralized health status management for all components.

- Aggregates health status from all registered components
- Provides async lifecycle management
- Exposes health and readiness endpoints via API
- Integrates with metrics and logging
"""

import asyncio
from typing import Dict, Any, List, Callable, Awaitable
from .schemas import HealthCheckDetail, HealthCheckResponse
from .utils import log_info
from .metrics import record_health_check

class HealthManager:
    def __init__(self):
        self._checks: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]] = {}
        self._lock = asyncio.Lock()

    async def setup(self):
        """
        Async setup logic for the HealthManager.
        """
        log_info("HealthManager: Setup complete.")

    async def shutdown(self):
        """
        Async shutdown logic for the HealthManager.
        """
        log_info("HealthManager: Shutdown complete.")

    def register_health_check(self, name: str, check: Callable[[], Awaitable[Dict[str, Any]]]) -> None:
        """
        Register an async health check function.
        """
        self._checks[name] = check
        log_info(f"HealthManager: Registered health check for '{name}'.")

    async def run_health_checks(self) -> Dict[str, HealthCheckDetail]:
        """
        Run all registered health checks and return results.
        """
        results: Dict[str, HealthCheckDetail] = {}
        for name, check in self._checks.items():
            try:
                result = await check()
                results[name] = HealthCheckDetail(**result)
            except Exception as e:
                results[name] = HealthCheckDetail(
                    status="fail",
                    details={"error": str(e)}
                )
        return results

    async def get_health_status(self) -> HealthCheckResponse:
        """
        Get overall health status of the application.
        """
        start_time = asyncio.get_event_loop().time()
        checks = await self.run_health_checks()
        overall_status = "ok" if all(c.status == "ok" for c in checks.values()) else "degraded"
        duration = asyncio.get_event_loop().time() - start_time
        record_health_check("status", duration)
        log_info(f"HealthManager: Health status: {overall_status}")
        return HealthCheckResponse(
            status=overall_status,
            checks=checks,
            uptime_seconds=0,  # Will be set by the app
            version="1.0.0"    # Will be set by the app
        )
