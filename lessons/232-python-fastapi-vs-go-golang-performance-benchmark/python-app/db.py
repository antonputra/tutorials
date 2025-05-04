import logging
import os
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, Optional

import aiomcache
import asyncpg
from fastapi import Depends, FastAPI, HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


POSTGRES_URI = POSTGRES_URI = os.environ["POSTGRES_URI"]
POSTGRES_POOL_SIZE = int(os.environ["POSTGRES_POOL_SIZE"])
MEMCACHED_HOST = os.environ["MEMCACHED_HOST"]
MEMCACHED_POOL_SIZE = os.environ["MEMCACHED_POOL_SIZE"]


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


PostgresDep = Annotated[asyncpg.Connection, Depends(get_db)]


class MemcachedClient:
    client: Optional[aiomcache.Client] = None

    @classmethod
    async def initialize(cls):
        """Initialize the Memcached client with connection pooling"""
        if not cls.client:
            cls.client = aiomcache.Client(
                host=MEMCACHED_HOST, pool_size=int(MEMCACHED_POOL_SIZE)
            )

    @classmethod
    async def close(cls):
        """Close the Memcached client"""
        if cls.client:
            await cls.client.close()
            cls.client = None

    @classmethod
    def get_client(cls) -> aiomcache.Client:
        """Get the Memcached client instance"""
        if not cls.client:
            raise HTTPException(
                status_code=503, detail="Memcached client is not initialized"
            )
        return cls.client


async def get_cache_client() -> AsyncGenerator[aiomcache.Client, None]:
    """Dependency for getting Memcached client"""
    client = MemcachedClient.get_client()
    try:
        yield client
    except aiomcache.exceptions.ClientException as e:
        raise HTTPException(status_code=503, detail=f"Memcached error: {str(e)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for database connection"""
    print(" Starting up database connection...")
    try:
        await db.create_pool()
        logger.info(" Database pool created successfully")
        await MemcachedClient.initialize()
        logger.info("Memcached Db pool created successfully")
        yield
    except Exception as e:
        logger.info(f"Failed to create database pool: {e}")
        raise
    finally:
        # Shutdown: close all connections
        logger.info(" Shutting down database connection...")
        await db.close()
        await MemcachedClient.close()
        logger.info(" Database connections closed")


MemcachedDep = Annotated[aiomcache.Client, Depends(get_cache_client)]