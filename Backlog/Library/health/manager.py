"""
Production-grade HealthManager with concurrent checks, timeouts, and detailed metrics.
"""

import asyncio
import time
from typing import Dict, Callable, Awaitable, Any
from .schemas import HealthCheckDetail, HealthCheckResponse
from .metrics import record_health_check, record_health_check_duration
from Library.logging import get_logger
from .exceptions import HealthCheckTimeoutError, HealthCheckFailedError

logger = get_logger(__name__)

class HealthManager:
    def __init__(self, version: str = "unknown", timeout: float = 5.0):
        self._checks: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]] = {}
        self._start_time = time.monotonic()
        self._version = version
        self._timeout = timeout
        self._lock = asyncio.Lock()

    async def setup(self):
        logger.info("HealthManager setup complete")

    async def shutdown(self):
        logger.info("HealthManager shutdown complete")

    def register_health_check(self, name: str, check: Callable[[], Awaitable[Dict[str, Any]]]) -> None:
        with self._lock:
            self._checks[name] = check
            logger.info(f"Registered health check: {name}")

    def unregister_health_check(self, name: str) -> None:
        with self._lock:
            if name in self._checks:
                del self._checks[name]
                logger.info(f"Unregistered health check: {name}")

    async def _run_check(self, name: str, check: Callable[[], Awaitable[Dict[str, Any]]]) -> HealthCheckDetail:
        start_time = time.monotonic()
        try:
            # Enforce timeout per health check
            result = await asyncio.wait_for(check(), timeout=self._timeout)
            status = result.get("status", "ok")
            details = result.get("details", {})
            
            # Record metrics
            duration = time.monotonic() - start_time
            record_health_check(name, status)
            record_health_check_duration(name, duration)
            
            return HealthCheckDetail(status=status, details=details)
        except asyncio.TimeoutError:
            record_health_check(name, "timeout")
            logger.warning(f"Health check timed out: {name}")
            return HealthCheckDetail(
                status="timeout",
                details={"error": f"Health check timed out after {self._timeout}s"}
            )
        except Exception as e:
            record_health_check(name, "fail")
            logger.error(f"Health check failed: {name} - {e}", exc_info=True)
            return HealthCheckDetail(
                status="fail",
                details={"error": str(e)}
            )

    async def run_health_checks(self) -> Dict[str, HealthCheckDetail]:
        """Run all checks concurrently with timeout enforcement"""
        tasks = {}
        async with self._lock:
            for name, check in self._checks.items():
                tasks[name] = asyncio.create_task(self._run_check(name, check))
        
        results = {}
        for name, task in tasks.items():
            results[name] = await task
        return results

    async def get_health_status(self) -> HealthCheckResponse:
        """Get overall health status with degraded state support"""
        checks = await self.run_health_checks()
        
        # Determine overall status
        if all(c.status == "ok" for c in checks.values()):
            overall_status = "ok"
        elif any(c.status == "fail" for c in checks.values()):
            overall_status = "fail"
        else:
            overall_status = "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            checks=checks,
            uptime_seconds=time.monotonic() - self._start_time,
            version=self._version
        )
