from fastapi import Request
from typing import Dict, Any

async def before_metrics(request: Request, **kwargs) -> Dict[str, Any]:
    # Example: Add a custom metric or check auth
    return {}

async def after_metrics(request: Request, response: Any, context: Dict[str, Any]):
    from core.logging import logger
    logger.info("Metrics scrape completed")
    return {}
