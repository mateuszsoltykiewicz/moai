"""
Pre- and post-hooks for health endpoints

- Used by base_endpoint_processor in /api/routers/health.py
- Can inject custom checks, audit, or enrich logs/metrics
"""

from fastapi import Request
from typing import Dict, Any

async def before_readyz(request: Request, **kwargs) -> Dict[str, Any]:
    """
    Pre-hook for /readyz endpoint.
    Can inject additional health checks.
    """
    # Example: Add a custom check
    custom_checks = {}
    try:
        # Simulate external API check (replace with real logic)
        # For demo, always ok
        custom_checks["external_api"] = {"status": "ok", "details": {"latency_ms": 42}}
    except Exception as e:
        custom_checks["external_api"] = {"status": "fail", "details": {"error": str(e)}}
    return {"custom_checks": custom_checks}

async def after_readyz(request: Request, response: Any, context: Dict[str, Any]):
    """
    Post-hook for /readyz endpoint.
    Can be used for audit logging or metrics enrichment.
    """
    # Example: Log the readiness result
    from core.logging import logger
    logger.info(f"Health post-hook: readiness probe returned {response.status}")
    # You can also push custom metrics or audit events here
    return {}
