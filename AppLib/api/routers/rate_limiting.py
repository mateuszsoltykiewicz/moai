"""
Rate Limiting API Router

- Get/set rate limiting configuration
- Check current rate limit status
- Dependency for per-user or per-IP rate limiting
"""

from fastapi import APIRouter, Depends, status, Request
from typing import Dict
from models.schemas import (
    RateLimitConfigRequest, RateLimitConfigResponse, RateLimitStatusResponse
)
from api.dependencies import get_current_user
from api.main import APIException
from sessions.redis import get_redis
import time
from metrics.rate_limiting import RATE_LIMIT_ALLOWED, RATE_LIMIT_BLOCKED

router = APIRouter(tags=["rate_limiting"])

# In-memory config for demonstration (replace with persistent store in prod)
RATE_LIMIT_CONFIGS: Dict[str, Dict] = {
    "user": {"limit": 100, "period_seconds": 60},
    "ip": {"limit": 50, "period_seconds": 60},
    "global": {"limit": 1000, "period_seconds": 60}
}

@router.get(
    "/config/{scope}",
    response_model=RateLimitConfigResponse,
    summary="Get rate limiting config"
)
async def get_rate_limit_config(scope: str, user=Depends(get_current_user)):
    config = RATE_LIMIT_CONFIGS.get(scope)
    if not config:
        raise APIException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"No rate limit config for scope: {scope}"
        )
    return RateLimitConfigResponse(scope=scope, **config)

@router.post(
    "/config",
    response_model=RateLimitConfigResponse,
    summary="Set rate limiting config"
)
async def set_rate_limit_config(
    req: RateLimitConfigRequest,
    user=Depends(get_current_user)
):
    RATE_LIMIT_CONFIGS[req.scope] = {
        "limit": req.limit,
        "period_seconds": req.period_seconds
    }
    return RateLimitConfigResponse(scope=req.scope, limit=req.limit, period_seconds=req.period_seconds)

async def rate_limit_dependency(
    request: Request,
    user=Depends(get_current_user),
    redis=Depends(get_redis),
    scope: str = "user"
):
    if scope == "user":
        identifier = user["username"]
    elif scope == "ip":
        identifier = request.client.host
    else:
        identifier = "global"

    config = RATE_LIMIT_CONFIGS.get(scope, RATE_LIMIT_CONFIGS["global"])
    key = f"ratelimit:{scope}:{identifier}"
    now = int(time.time())
    ttl = config["period_seconds"]

    current = await redis.get(key)
    if current is None:
        await redis.set(key, 1, expire=ttl)
        remaining = config["limit"] - 1
        allowed = True
        RATE_LIMIT_ALLOWED.labels(scope=scope).inc()
    else:
        current = int(current)
        if current < config["limit"]:
            await redis.incr(key)
            remaining = config["limit"] - (current + 1)
            allowed = True
            RATE_LIMIT_ALLOWED.labels(scope=scope).inc()
        else:
            ttl_remaining = await redis.ttl(key)
            RATE_LIMIT_BLOCKED.labels(scope=scope).inc()
            raise APIException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                message="Rate limit exceeded.",
                details={"reset_in": ttl_remaining}
            )

    return RateLimitStatusResponse(
        allowed=allowed,
        remaining=remaining,
        reset_in=ttl
    )

@router.get(
    "/status/{scope}",
    response_model=RateLimitStatusResponse,
    summary="Check current rate limit status"
)
async def rate_limit_status(
    scope: str,
    request: Request,
    user=Depends(get_current_user),
    redis=Depends(get_redis)
):
    try:
        return await rate_limit_dependency(request, user, redis, scope)
    except APIException as e:
        return RateLimitStatusResponse(
            allowed=False,
            remaining=0,
            reset_in=e.details.get("reset_in", 0)
        )
