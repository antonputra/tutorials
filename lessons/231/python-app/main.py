import datetime
import logging
import os
import time
import uuid

from asyncpg import PostgresError
from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse, PlainTextResponse
from prometheus_client import make_asgi_app
from pydantic import BaseModel
from pymemcache.client.base import Client

from db import PostgresDep, lifespan
from metrics import H

app = FastAPI(lifespan=lifespan)

MEMCACHED_HOST = os.environ["MEMCACHED_HOST"]
cache_client = Client(MEMCACHED_HOST)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Disable access logs to match Go implementation
block_endpoints = ["/api/devices", "/metrics/", "/metrics"]


class LogFilter(logging.Filter):
    def filter(self, record):
        if record.args and len(record.args) >= 3:
            if record.args[2] in block_endpoints:
                return False
        return True


uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.addFilter(LogFilter())


@app.get("/healthz", response_class=PlainTextResponse)
def health():
    return "OK"


@app.get("/api/devices", response_class=ORJSONResponse)
def get_devices():
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

    return devices


class DeviceRequest(BaseModel):
    mac: str
    firmware: str


@app.post("/api/devices", status_code=201, response_class=ORJSONResponse)
async def create_device(device: DeviceRequest, conn: PostgresDep):
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        device_uuid = uuid.uuid4()

        insert_query = """
            INSERT INTO python_device (uuid, mac, firmware, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, uuid, mac, firmware, created_at, updated_at;
            """

        start_time = time.perf_counter()

        row = await conn.fetchrow(
            insert_query, device_uuid, device.mac, device.firmware, now, now
        )

        H.labels(op="insert", db="postgres").observe(time.perf_counter() - start_time)

        device_dict = dict(row)

        # Measure cache operation
        start_time = time.perf_counter()
        cache_client.set(str(device_uuid), device_dict, expire=20)
        H.labels(op="set", db="memcache").observe(time.perf_counter() - start_time)

        return row

    except PostgresError as e:
        raise HTTPException(
            status_code=500, detail="Database error occurred while creating device"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred while creating device"
        )
