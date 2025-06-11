# subservices/auth/service.py
from fastapi import HTTPException, status
from jose import JWTError, jwt
from jose.utils import base64url_decode
import httpx

class AuthService:
    def __init__(self, jwks_url: str):
        self.jwks_url = jwks_url
        self._jwks_cache = None

    async def fetch_jwks(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url)
            self._jwks_cache = response.json()
            return self._jwks_cache

    async def validate_token(self, token: str):
        if not self._jwks_cache:
            await self.fetch_jwks()
            
        # JWT header extraction
        try:
            header = jwt.get_unverified_header(token)
            kid = header["kid"]
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token header: {str(e)}"
            )
            
        # Find matching key
        key = next((k for k in self._jwks_cache["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No matching JWK found for token"
            )
            
        # Validate token
        try:
            return jwt.decode(
                token,
                key,
                algorithms=[key["alg"]],
                audience="your-api-audience",
                issuer="your-token-issuer"
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )
