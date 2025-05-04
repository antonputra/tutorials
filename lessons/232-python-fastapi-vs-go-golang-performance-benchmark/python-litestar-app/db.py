from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import aiomcache
import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


POSTGRES_URI = os.environ["POSTGRES_URI"]
POSTGRES_POOL_SIZE = int(os.environ["POSTGRES_POOL_SIZE"])
MEMCACHED_HOST = os.environ["MEMCACHED_HOST"]
MEMCACHED_POOL_SIZE = int(os.environ["MEMCACHED_POOL_SIZE"])


class Database:
    __slots__ = ("_pool",)

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    @staticmethod
    async def from_postgres() -> Database:
        """Create connection pool if it doesn't exist"""
        try:
            pool = await asyncpg.create_pool(
                POSTGRES_URI,
                min_size=10,
                max_size=POSTGRES_POOL_SIZE,
                max_inactive_connection_lifetime=300,
            )
            logger.info("Database pool created: %s", pool)

            return Database(pool)
        except asyncpg.exceptions.PostgresError as e:
            logging.error(f"Error creating PostgreSQL connection pool: {e}")
            raise ValueError("Failed to create PostgreSQL connection pool")
        except Exception as e:
            logging.error(f"Unexpected error while creating connection pool: {e}")
            raise

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get database connection from pool"""
        async with self._pool.acquire() as connection:
            logger.info("Connection acquired from pool")
            yield connection
            logger.info("Connection released back to pool")

    async def close(self):
        """Close the pool when shutting down"""
        await self._pool.close()
        logger.info("Database pool closed")


class MemcachedClient:
    __slots__ = ("_client",)

    def __init__(self, client: aiomcache.Client):
        self._client = client

    @staticmethod
    async def initialize() -> MemcachedClient:
        """Initialize the Memcached client with connection pooling"""
        try:
            client = aiomcache.Client(
                host=MEMCACHED_HOST, pool_size=MEMCACHED_POOL_SIZE
            )
            logger.info(f"Memcached client created: {client}")
            return MemcachedClient(client)
        except Exception:
            logging.exception("Error creating Memcached client")
            raise ValueError("Failed to create Memcached client")

    async def close(self):
        """Close the Memcached client"""
        await self._client.close()
        logger.info("Memcached client closed")

    def get_client(self) -> aiomcache.Client:
        """Get the Memcached client instance"""
        return self._client
