import asyncio
from typing import Optional, Dict
from jose import JWTError, jwt
from jose.constants import ALGORITHMS
import httpx
import time

from core.config import AsyncConfigManager
from core.logging import get_logger
from metrics.oauth import (
    OAUTH_TOKEN_VALIDATIONS,
    OAUTH_ERRORS,
    OAUTH_TOKEN_VALIDATION_TIME
)

logger = get_logger(__name__)

class OAuthAdapter:
    def __init__(self, config_manager: AsyncConfigManager):
        self.config_manager = config_manager
        self._jwks_client = None

    async def get_jwks(self) -> Dict:
        """Fetch JWKS from OAuth provider"""
        config = await self.config_manager.get()
        async with httpx.AsyncClient() as client:
            response = await client.get(config.oauth.jwks_uri)
            return response.json()

    async def validate_token(self, token: str) -> Dict:
        """Validate JWT token and return claims"""
        start = time.monotonic()
        try:
            config = await self.config_manager.get()
            jwks = await self.get_jwks()
            
            OAUTH_TOKEN_VALIDATIONS.inc()
            claims = jwt.decode(
                token,
                jwks,
                algorithms=[ALGORITHMS.RS256],
                audience=config.oauth.audience,
                issuer=config.oauth.issuer
            )
            
            OAUTH_TOKEN_VALIDATION_TIME.observe(time.monotonic() - start)
            return claims
        except JWTError as e:
            OAUTH_ERRORS.inc()
            logger.error(f"Token validation failed: {str(e)}")
            raise
        except httpx.HTTPError as e:
            OAUTH_ERRORS.inc()
            logger.error(f"JWKS fetch failed: {str(e)}")
            raise

    async def get_user_info(self, token: str) -> Dict:
        """Fetch user info from OAuth provider"""
        config = await self.config_manager.get()
        async with httpx.AsyncClient() as client:
            response = await client.get(
                config.oauth.userinfo_endpoint,
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.json()
