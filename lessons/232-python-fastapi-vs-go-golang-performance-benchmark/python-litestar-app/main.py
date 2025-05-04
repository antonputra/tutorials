import datetime
import logging
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass

import aiomcache
import orjson
from asyncpg import PostgresError
from litestar import Litestar, Request, get, post
from litestar.exceptions import HTTPException
from litestar.logging import LoggingConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from pydantic import BaseModel

from db import Database, MemcachedClient
from metrics import H

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging_config = LoggingConfig(
    root={"level": "ERROR", "handlers": ["queue_listener"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    log_exceptions="always",
)


@dataclass(slots=True)
class DeviceRequest(BaseModel):
    mac: str
    firmware: str


H_MEMCACHED_LABEL = H.labels(op="set", db="memcache")
H_POSTGRES_LABEL = H.labels(op="insert", db="postgres")
INSERT_QUERY = """
    INSERT INTO python_device (uuid, mac, firmware, created_at, updated_at)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING id;
"""


@get("/healthz")
async def healthz_handler(request: Request) -> str:
    return "OK"


@get("/api/devices")
async def get_devices_handler(request: Request) -> list[dict]:
    return [
        {
            "id": 1,
            "uuid": "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
            "mac": "EF-2B-C4-F5-D6-34",
            "firmware": "2.1.5",
            "created_at": "2024-05-28T15:21:51.137Z",
            "updated_at": "2024-05-28T15:21:51.137Z",
        },
        {
            "id": 2,
            "uuid": "d2293412-36eb-46e7-9231-af7e9249fffe",
            "mac": "E7-34-96-33-0C-4C",
            "firmware": "1.0.3",
            "created_at": "2024-01-28T15:20:51.137Z",
            "updated_at": "2024-01-28T15:20:51.137Z",
        },
        {
            "id": 3,
            "uuid": "eee58ca8-ca51-47a5-ab48-163fd0e44b77",
            "mac": "68-93-9B-B5-33-B9",
            "firmware": "4.3.1",
            "created_at": "2024-08-28T15:18:21.137Z",
            "updated_at": "2024-08-28T15:18:21.137Z",
        },
    ]


@post("/api/devices")
async def create_device_handler(data: DeviceRequest, request: Request) -> dict:
    device_request = data
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        device_uuid = uuid.uuid4()

        start_time = time.perf_counter()
        async with request.app.state.db.get_connection() as conn:
            row = await conn.fetchrow(
                INSERT_QUERY,
                device_uuid,
                device_request.mac,
                device_request.firmware,
                now,
                now,
            )

        H_POSTGRES_LABEL.observe(time.perf_counter() - start_time)

        if not row:
            raise HTTPException(
                status_code=500, detail="Failed to create device record"
            )

        device_dict = {
            "id": row["id"],
            "uuid": str(device_uuid),
            "mac": device_request.mac,
            "firmware": device_request.firmware,
            "created_at": now,
            "updated_at": now,
        }

        start_time = time.perf_counter()
        cache_client = request.app.state.memcached.get_client()
        await cache_client.set(
            device_uuid.hex.encode(),
            orjson.dumps(device_dict),
            exptime=20,
        )
        H_MEMCACHED_LABEL.observe(time.perf_counter() - start_time)

        return device_dict

    except PostgresError:
        logger.exception("Postgres error")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except aiomcache.exceptions.ClientException:
        logger.exception("Memcached error")
        raise HTTPException(status_code=500, detail="Memcached error occurred")
    except Exception:
        logger.exception("Unknown error")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@get("/api/devices/stats")
async def get_device_stats_handler(request: Request) -> dict:
    try:
        cache_client = request.app.state.memcached.get_client()
        stats = await cache_client.stats()
        return {
            "curr_items": stats.get(b"curr_items", 0),
            "total_items": stats.get(b"total_items", 0),
            "bytes": stats.get(b"bytes", 0),
            "curr_connections": stats.get(b"curr_connections", 0),
            "get_hits": stats.get(b"get_hits", 0),
            "get_misses": stats.get(b"get_misses", 0),
        }
    except aiomcache.exceptions.ClientException:
        logger.exception("Memcached error")
        raise HTTPException(status_code=500, detail="Memcached error occurred")
    except Exception:
        logger.exception("Unknown error")
        raise HTTPException(status_code=500, detail="Unexpected error occurred")


@asynccontextmanager
async def lifespan(app: Litestar):
    app.state.db = await Database.from_postgres()
    app.state.memcached = await MemcachedClient.initialize()
    try:
        yield
    finally:
        await app.state.db.close()
        await app.state.memcached.close()


app = Litestar(
    route_handlers=[
        healthz_handler,
        get_devices_handler,
        create_device_handler,
        get_device_stats_handler,
    ],
    lifespan=[lifespan],
    openapi_config=OpenAPIConfig(
        title="Litestar Example",
        description="Example of Litestar with Scalar OpenAPI docs",
        version="0.0.1",
        render_plugins=[SwaggerRenderPlugin(version="5.1.3")],
        path="/docs",
    ),
    logging_config=logging_config,
)
