import datetime
import logging
import os
import time
import uuid

import aiomcache
import orjson
from asyncpg import PostgresError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.exceptions import HTTPException
from starlette.routing import Route, Mount
from prometheus_client import make_asgi_app
from pydantic import BaseModel

from db import db, lifespan
from metrics import H


MEMCACHED_HOST = os.environ["MEMCACHED_HOST"]
cache_client = aiomcache.Client(MEMCACHED_HOST)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ORJSONResponse(Response):
    media_type = "application/json"

    def render(self, content) -> bytes:
        return orjson.dumps(
            content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY
        )


def health(request: Request):
    return PlainTextResponse("OK")


def get_devices(request: Request):
    devices = [
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

    return ORJSONResponse(content=devices)


class DeviceRequest(BaseModel):
    mac: str
    firmware: str


async def create_device(request: Request):
    device = DeviceRequest.model_validate(orjson.loads(await request.body()))
    try:
        now = datetime.datetime.now()
        device_uuid = uuid.uuid4()

        insert_query = """
            INSERT INTO python_device (uuid, mac, firmware, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, uuid, mac, firmware, created_at, updated_at;
            """

        start_time = time.perf_counter()

        async with db.get_connection() as conn:
            row = await conn.fetchrow(
                insert_query, device_uuid.hex, device.mac, device.firmware, now, now
            )

        H.labels(op="insert", db="postgres").observe(time.perf_counter() - start_time)

        device_dict = dict(row)

        # Measure cache operation
        start_time = time.perf_counter()

        await cache_client.set(
            device_uuid.hex.encode(),
            orjson.dumps(device_dict),
            exptime=20,
        )

        H.labels(op="set", db="memcache").observe(time.perf_counter() - start_time)

        return ORJSONResponse(content=device_dict, status_code=201)

    except PostgresError:
        logger.exception("kaka")
        raise HTTPException(
            status_code=500, detail="Database error occurred while creating device"
        )
    except aiomcache.exceptions.ClientException:
        logger.exception("kaka")
        raise HTTPException(
            status_code=500,
            detail="Memcached Database error occurred while creating device",
        )
    except Exception:
        logger.exception("kaka")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred while creating device"
        )


routes = [
    Route("/healthz", endpoint=health),
    Route("/api/devices", endpoint=get_devices, methods=["GET"]),
    Route("/api/devices", endpoint=create_device, methods=["POST"]),
    Mount("/metrics", make_asgi_app()),
]


app = Starlette(lifespan=lifespan, routes=routes)
