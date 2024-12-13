import os
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

POSTGRES_URI = os.environ["POSTGRES_URI"]
POSTGRES_POOL_SIZE = int(os.environ["POSTGRES_POOL_SIZE"])


engine = create_async_engine(
    POSTGRES_URI,
    echo=False,
    pool_pre_ping=False,
    pool_size=POSTGRES_POOL_SIZE,
    max_overflow=0,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_postgres_session():
    async with async_session() as session:
        yield session


PostgresDep = Annotated[AsyncSession, Depends(get_postgres_session)]
