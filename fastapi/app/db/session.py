from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

async_engine = create_async_engine(
    settings.DATABASE_URL_ASYNC, 
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

sync_engine = create_engine(
    settings.DATABASE_URL_SYNC.replace("+asyncpg", "+psycopg2"),
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
    autoflush=False,)

def get_sync_db():
    """Контекстный менеджер для синхронного использования"""
    with SyncSessionLocal() as session:
        yield session