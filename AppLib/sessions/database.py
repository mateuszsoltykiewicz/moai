from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from core.config import AsyncConfigManager

_engine = None
_SessionLocal = None

async def init_engine_and_session():
    global _engine, _SessionLocal
    config = await AsyncConfigManager.get()
    db_url = config.database.url
    _engine = create_async_engine(db_url, echo=False, future=True)
    _SessionLocal = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    global _SessionLocal
    if _SessionLocal is None:
        await init_engine_and_session()
    async with _SessionLocal() as session:
        yield session
