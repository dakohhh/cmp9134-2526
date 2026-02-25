
from fastapi import Depends
from sqlmodel import SQLModel
from settings.config import settings
from typing import Annotated, AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio.session import _AsyncSessionBind

# Import model registry to ensure all models are registered with SQLAlchemy
# This must happen before any database operations to resolve string relationships
import app.database.registry  # noqa: F401

# Convert DB URI for async drivers
_uri = settings.DATABASE_URL
if _uri.startswith("postgresql://"):
    _uri = _uri.replace("postgresql://", "postgresql+asyncpg://", 1)
elif _uri.startswith("sqlite"):
    _uri = _uri.replace("sqlite://", "sqlite+aiosqlite://", 1)
async_database_uri = _uri

engine = create_async_engine(async_database_uri, pool_pre_ping=True, connect_args={"check_same_thread": False} if "sqlite" in _uri else {})

class CustomAsyncSession(AsyncSession):
    def __init__(self, bind: _AsyncSessionBind) -> None:
        super().__init__(bind=bind)

async def get_session() -> AsyncGenerator[CustomAsyncSession, None]:
    async with CustomAsyncSession(engine) as session:
        yield session


def get_cli_session() -> CustomAsyncSession:
    engine = create_async_engine(async_database_uri, pool_pre_ping=True, poolclass=NullPool , connect_args={"check_same_thread": False} if "sqlite" in _uri else {})
    return CustomAsyncSession(engine)


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


DatabaseSession = Annotated[CustomAsyncSession, Depends(get_session)]