"""
Async Database Session Management for AppLib

- Provides get_db_session dependency for FastAPI
- Uses SQLAlchemy async engine and sessionmaker
- Supports config-driven DB URL and pool settings
- Handles session lifecycle (commit/rollback/close)
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine, async_sessionmaker
)
from sqlalchemy.orm import sessionmaker
from core.config import get_config
from fastapi import Depends
from contextlib import asynccontextmanager

# Create engine and sessionmaker globally (singleton pattern)
_engine = None
_AsyncSessionLocal = None

def init_engine():
    global _engine, _AsyncSessionLocal
    config = get_config().database
    # Example: "postgresql+asyncpg://user:password@host/dbname"
    db_url = config.url
    _engine = create_async_engine(
        db_url,
        echo=getattr(config, "echo", False),
        pool_size=getattr(config, "pool_size", 5),
        max_overflow=getattr(config, "max_overflow", 10),
        future=True
    )
    _AsyncSessionLocal = async_sessionmaker(
        bind=_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

# Call this once at app startup
def setup_database():
    if not _engine or not _AsyncSessionLocal:
        init_engine()

@asynccontextmanager
async def get_db_session():
    """
    Async dependency for FastAPI endpoints.
    Usage: db=Depends(get_db_session)
    """
    if not _AsyncSessionLocal:
        setup_database()
    session = _AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
