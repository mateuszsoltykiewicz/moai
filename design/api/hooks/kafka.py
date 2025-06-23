from fastapi import Request
from typing import Dict, Any

async def before_publish(request: Request, **kwargs) -> Dict[str, Any]:
    body = await request.json()
    if len(body.get("value", {})) > 1000:
        return {"validation_result": {"valid": False, "message": "Message too large"}}
    return {"validation_result": {"valid": True}}

async def after_publish(request: Request, response: Any, context: Dict[str, Any]):
    from core.logging import logger
    logger.info(f"Kafka post-hook: published to {response.topic}")
    return {}
