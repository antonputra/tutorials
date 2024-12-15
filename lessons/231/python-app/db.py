import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg
from starlette.applications import Starlette

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

POSTGRES_URI = os.environ["POSTGRES_URI"]
POSTGRES_POOL_SIZE = int(os.environ["POSTGRES_POOL_SIZE"])


class Database:
    def __init__(self):
        self.pool = None

    async def create_pool(self):
        """Create connection pool if it doesn't exist"""
        if self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(
                    POSTGRES_URI,
                    min_size=10,
                    max_size=POSTGRES_POOL_SIZE,
                    max_inactive_connection_lifetime=300,
                )
                logger.info(f"Database pool created: {self.pool}")
            except asyncpg.exceptions.PostgresError as e:
                logging.error(f"Error creating PostgreSQL connection pool: {e}")
                raise ValueError("Failed to create PostgreSQL connection pool")
            except Exception as e:
                logging.error(f"Unexpected error while creating connection pool: {e}")
                raise

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get database connection from pool"""
        if not self.pool:
            await self.create_pool()
        async with self.pool.acquire() as connection:
            logger.info("Connection acquired from pool")
            yield connection
            logger.info("Connection released back to pool")

    async def close(self):
        """Close the pool when shutting down"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
            self.pool = None


db = Database()


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    async with db.get_connection() as conn:
        yield conn


@asynccontextmanager
async def lifespan(app: Starlette):
    """Lifespan context manager for database connection"""
    print(" Starting up database connection...")
    try:
        await db.create_pool()
        logger.info(" Database pool created successfully")
        yield
    except Exception as e:
        logger.info(f"Failed to create database pool: {e}")
        raise
    finally:
        # Shutdown: close all connections
        logger.info(" Shutting down database connection...")
        await db.close()
        logger.info(" Database connections closed")
