import os

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession


POSTGRES_URI = os.environ["POSTGRES_URI"]
POSTGRES_POOL_SIZE = int(os.environ["POSTGRES_POOL_SIZE"])


engine = create_async_engine(POSTGRES_URI, pool_size=POSTGRES_POOL_SIZE)


async def get_postgres_session():
    async with AsyncSession(engine) as session:
        yield session


PostgresDep = Annotated[AsyncSession, Depends(get_postgres_session)]
