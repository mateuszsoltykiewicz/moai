from fastapi import Request
from typing import Dict, Any

async def before_update(request: Request, **kwargs) -> Dict[str, Any]:
    body = await request.json()
    if not body.get("path") or not body.get("value"):
        return {"validation_result": {"valid": False, "message": "Missing path or value"}}
    return {"validation_result": {"valid": True}}

async def after_update(request: Request, response: Any, context: Dict[str, Any]):
    from core.logging import logger
    logger.info(f"Secret updated at {response.path} by {context['user'].sub}")
    return {}
