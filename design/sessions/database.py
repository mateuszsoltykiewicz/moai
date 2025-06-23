"""
Async Database Session Manager

- Manages async database connections and pooling.
- Provides context manager interface for safe resource handling.
- Integrates with SQLAlchemy's async engine and sessionmaker.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import AsyncGenerator, Optional
import logging

class DatabaseSessionManager:
    def __init__(self, db_url: str, echo: bool = False, pool_size: int = 5):
        self.engine = create_async_engine(
            db_url,
            echo=echo,
            pool_size=pool_size,
            future=True
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        self.logger = logging.getLogger("DatabaseSessionManager")

    async def __aenter__(self) -> AsyncSession:
        try:
            self.session = self.session_factory()
            return self.session
        except SQLAlchemyError as exc:
            self.logger.error(f"Failed to create DB session: {exc}")
            raise

    async def __aexit__(self, exc_type, exc, tb):
        try:
            await self.session.close()
        except Exception as exc:
            self.logger.warning(f"Error closing DB session: {exc}")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Async generator for dependency injection frameworks (e.g., FastAPI).
        Usage:
            async for session in db_manager.get_session():
                ...
        """
        async with self as session:
            yield session
