import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from .schemas import ExceptionPayload
from Library.logging import get_logger
from Library.config import get_config  # Assume config component

logger = get_logger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def forward_exception(payload: ExceptionPayload):
    """Forward exception to central server with retry logic"""
    try:
        config = get_config()
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.post(
                f"{config.exception_server_url}/exceptions/submit",
                json=payload.dict(),
                headers={"Authorization": f"Bearer {config.exception_server_token}"}
            )
            response.raise_for_status()
    except Exception as e:
        logger.error(f"Exception forwarding failed: {str(e)}")
        # Fallback: Log to local error aggregator (Sentry, etc.)
        logger.error(f"Failed exception payload: {payload.dict()}")
