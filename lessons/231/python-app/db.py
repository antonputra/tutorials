import os
from typing import Annotated, AsyncGenerator

import asyncpg
import asyncpg.transaction
from fastapi import Depends

POSTGRES_URI = os.environ["POSTGRES_URI"]
POSTGRES_POOL_SIZE = int(os.environ["POSTGRES_POOL_SIZE"])


_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            POSTGRES_URI, command_timeout=60, max_size=POSTGRES_POOL_SIZE
        )
    return _pool


async def get_postgres_session() -> (
    AsyncGenerator[tuple[asyncpg.Connection, asyncpg.transaction.Transaction], None]
):
    global _pool
    if _pool is None:
        _pool = await get_pool()
    async with _pool.acquire() as conn:
        tr = conn.transaction()
        await tr.start()
        yield conn, tr


PostgresDep = Annotated[
    tuple[asyncpg.Connection, asyncpg.transaction.Transaction],
    Depends(get_postgres_session),
]
