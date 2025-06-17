"""
HTTP/External API Session Manager

- Manages persistent HTTP connections for external API calls.
- Supports async (httpx.AsyncClient) and sync (requests.Session) usage.
- Centralizes configuration for headers, timeouts, and retries.
- Context manager interface for safe resource handling.
"""

import httpx
from typing import Optional, Dict, Any
import logging

class HTTPSessionManager:
    def __init__(
        self,
        base_url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = 10.0,
        retries: int = 3,
        verify: bool = True,
        sync: bool = False,
    ):
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = timeout
        self.retries = retries
        self.verify = verify
        self.sync = sync
        self.logger = logging.getLogger("HTTPSessionManager")
        self.client: Optional[httpx.AsyncClient] = None
        self.sync_client: Optional[httpx.Client] = None

    async def __aenter__(self) -> httpx.AsyncClient:
        self.client = httpx.AsyncClient(
            base_url=self.base_url or "",
            headers=self.headers,
            timeout=self.timeout,
            verify=self.verify,
        )
        self.logger.info("Async HTTP client started.")
        return self.client

    async def __aexit__(self, exc_type, exc, tb):
        if self.client:
            await self.client.aclose()
            self.logger.info("Async HTTP client closed.")

    def __enter__(self) -> httpx.Client:
        self.sync_client = httpx.Client(
            base_url=self.base_url or "",
            headers=self.headers,
            timeout=self.timeout,
            verify=self.verify,
        )
        self.logger.info("Sync HTTP client started.")
        return self.sync_client

    def __exit__(self, exc_type, exc, tb):
        if self.sync_client:
            self.sync_client.close()
            self.logger.info("Sync HTTP client closed.")

    # Optional: Retry logic can be added via httpx middleware or custom wrapper

