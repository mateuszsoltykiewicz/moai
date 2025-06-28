"""
API endpoints for RedisManager (diagnostics and simple ops).
"""

from fastapi import APIRouter, HTTPException, Body, Query, Depends, Request
from .manager import RedisManager
from .schemas import RedisStatusResponse, RedisKVRequest
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/redis", tags=["redis"])
redis_manager: RedisManager = None  # Set this at app startup

@router.get("/status", response_model=RedisStatusResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "redis", "read"))])
async def get_status():
    if not redis_manager:
        logger.error("RedisManager not initialized")
        raise HTTPException(503, "RedisManager not initialized")
    healthy = await redis_manager.health_check()
    return RedisStatusResponse(status="ok" if healthy else "fail")

@router.get("/kv", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "redis", "read"))])
async def get_kv(key: str = Query(...)):
    if not redis_manager:
        logger.error("RedisManager not initialized")
        raise HTTPException(503, "RedisManager not initialized")
    value = await redis_manager.get(key)
    return {"key": key, "value": value}

@router.post("/kv", dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "redis", "write"))])
async def set_kv(req: RedisKVRequest = Body(...)):
    if not redis_manager:
        logger.error("RedisManager not initialized")
        raise HTTPException(503, "RedisManager not initialized")
    await redis_manager.set(req.key, req.value, expire=req.expire)
    return {"result": "ok"}
