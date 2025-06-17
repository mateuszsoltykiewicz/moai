"""
Health and readiness endpoint utilities.

- Aggregate health status from dependencies.
- Expose /health and /ready endpoints.
"""

from typing import Dict, Callable

def basic_health_check() -> Dict:
    return {"status": "ok"}

def aggregate_health_checks(checks: Dict[str, Callable[[], Dict]]) -> Dict:
    """
    Run all health checks and aggregate results.
    """
    status = "ok"
    results = {}
    for name, check in checks.items():
        try:
            result = check()
            if result.get("status") != "ok":
                status = "degraded"
            results[name] = result
        except Exception as exc:
            status = "error"
            results[name] = {"status": "error", "error": str(exc)}
    return {"status": status, "checks": results}
