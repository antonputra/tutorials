from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

import asyncpg
from fastapi import Depends, FastAPI

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


config = Config("config.yaml")


class Database:
    __slots__ = ("_pool",)

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    @staticmethod
    async def from_postgres() -> Database:
        try:
            pool = await asyncpg.create_pool(
                host=config.db.host,
                user=config.db.user,
                password=config.db.password,
                database=config.db.database,
                min_size=10,
                max_size=config.db.max_connections,
                max_inactive_connection_lifetime=300,
            )

            return Database(pool)
        except asyncpg.exceptions.PostgresError:
            raise ValueError("Failed to create PostgreSQL connection pool")
        except Exception:
            raise

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        async with self._pool.acquire() as connection:
            yield connection

    async def close(self):
        await self._pool.close()


db: Database


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    async with db.get_connection() as conn:
        yield conn


PostgresDep = Annotated[asyncpg.Connection, Depends(get_db)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        global db
        db = await Database.from_postgres()
        yield
    except Exception:
        logger.exception("Failed to create database pool")
        raise
    finally:
        await db.close()
        logger.info("Database connections closed")
