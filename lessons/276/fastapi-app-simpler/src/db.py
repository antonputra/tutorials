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


async def init_postgres() -> None:
    global pool
    try:
        pool = await asyncpg.create_pool(
            host=config.db.host,
            user=config.db.user,
            password=config.db.password,
            database=config.db.database,
            min_size=config.db.max_connections,
            max_size=config.db.max_connections,
            max_inactive_connection_lifetime=300,
        )
    except asyncpg.exceptions.PostgresError:
        raise ValueError("Failed to create PostgreSQL connection pool")
    except Exception:
        raise


pool: asyncpg.Pool


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    global pool
    async with pool.acquire() as connection:
        yield connection


PostgresDep = Annotated[asyncpg.Connection, Depends(get_db, use_cache=False)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_postgres()
        yield
    except Exception:
        logger.exception("Failed to create database pool")
        raise
    finally:
        await pool.close()
        logger.info("Database connections closed")
