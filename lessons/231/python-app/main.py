import datetime
import logging
import os
import time
import uuid

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, PlainTextResponse
from prometheus_client import make_asgi_app
from pymemcache.client.base import Client
from sqlalchemy import insert
from asyncer import asyncify
from db import PostgresDep
from metrics import H
from models import Device

app = FastAPI()

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


@app.post("/api/devices", status_code=201, response_class=ORJSONResponse)
async def create_device(device: Device, session: PostgresDep) -> Device:
    # To match Go implementation instead of using SQLAlchemy  factory.
    now = datetime.datetime.now(datetime.timezone.utc)
    device_uuid = uuid.uuid4()

    stmt = (
        insert(Device)
        .values(
            uuid=device_uuid,
            mac=device.mac,
            firmware=device.firmware,
            created_at=now,
            updated_at=now,
        )
        .returning(Device)
    )

    # Measure the same insert operation as in Go
    start_time = time.perf_counter()
    device_result = await session.execute(stmt)
    device_dict = device_result.mappings().one()
    await session.commit()
    H.labels(op="insert", db="postgres").observe(time.perf_counter() - start_time)

    # Measure the same set operation as in Go
    start_time = time.perf_counter()
    cache_client.set(str(device_uuid), dict(device_dict), expire=20)
    H.labels(op="set", db="memcache").observe(time.perf_counter() - start_time)

    return device_dict
