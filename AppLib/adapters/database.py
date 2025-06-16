import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import AsyncConfigManager
from core.logging import get_logger
from metrics.database import (
    DB_CONNECTIONS,
    DB_QUERIES,
    DB_ERRORS,
    DB_QUERY_TIME
)

logger = get_logger(__name__)

class AsyncDatabase:
    def __init__(self, config_manager: AsyncConfigManager):
        self.config_manager = config_manager
        self.engine = None
        self.async_session = None

    async def connect(self):
        """Initialize database connection pool"""
        config = await self.config_manager.get()
        self.engine = create_async_engine(
            config.database.url,
            pool_size=config.database.pool_size,
            max_overflow=config.database.max_overflow,
            pool_timeout=config.database.pool_timeout
        )
        self.async_session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )
        DB_CONNECTIONS.inc()

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Async context manager for database sessions"""
        if not self.async_session:
            await self.connect()
        
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                DB_ERRORS.inc()
                logger.error(f"Database error: {str(e)}")
                raise
            finally:
                await session.close()

    async def execute(self, query, **params):
        """Execute raw SQL with metrics"""
        start = time.monotonic()
        try:
            async with self.session() as session:
                result = await session.execute(query, params)
                DB_QUERIES.inc()
                DB_QUERY_TIME.observe(time.monotonic() - start)
                return result
        except Exception as e:
            DB_ERRORS.inc()
            raise

    async def close(self):
        """Close all connections"""
        if self.engine:
            await self.engine.dispose()
            DB_CONNECTIONS.dec()
