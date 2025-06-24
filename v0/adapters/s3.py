import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional
import aioboto3
from botocore.exceptions import BotoCoreError

from core.config import AsyncConfigManager
from core.logging import get_logger
from metrics.s3 import (
    S3_UPLOADS,
    S3_DOWNLOADS,
    S3_ERRORS,
    S3_OPERATION_TIME
)

logger = get_logger(__name__)

class S3Adapter:
    def __init__(self, config_manager: AsyncConfigManager):
        self.config_manager = config_manager
        self.session = aioboto3.Session()

    @asynccontextmanager
    async def client_context(self) -> AsyncIterator[aioboto3.S3.Client]:
        """Async context manager for S3 client"""
        config = await self.config_manager.get()
        async with self.session.client(
            "s3",
            endpoint_url=config.s3.endpoint,
            aws_access_key_id=config.s3.access_key,
            aws_secret_access_key=config.s3.secret_key,
            region_name=config.s3.region
        ) as client:
            yield client

    async def upload_file(self, bucket: str, key: str, data: bytes) -> None:
        """Upload file to S3 with metrics"""
        start = time.monotonic()
        try:
            async with self.client_context() as client:
                await client.put_object(Bucket=bucket, Key=key, Body=data)
                S3_UPLOADS.inc()
                S3_OPERATION_TIME.observe(time.monotonic() - start)
        except BotoCoreError as e:
            S3_ERRORS.inc()
            logger.error(f"S3 upload failed: {str(e)}")
            raise

    async def download_file(self, bucket: str, key: str) -> bytes:
        """Download file from S3 with metrics"""
        start = time.monotonic()
        try:
            async with self.client_context() as client:
                response = await client.get_object(Bucket=bucket, Key=key)
                data = await response["Body"].read()
                S3_DOWNLOADS.inc()
                S3_OPERATION_TIME.observe(time.monotonic() - start)
                return data
        except BotoCoreError as e:
            S3_ERRORS.inc()
            logger.error(f"S3 download failed: {str(e)}")
            raise

    async def generate_presigned_url(self, bucket: str, key: str, expires: int = 3600) -> str:
        """Generate presigned URL for temporary access"""
        async with self.client_context() as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires
            )
