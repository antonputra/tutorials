import datetime
import logging
import os
import time
import uuid

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, PlainTextResponse
from prometheus_client import make_asgi_app
from pymemcache.client.base import Client

from db import PostgresDep
from metrics import H
from models import Device

app = FastAPI()

MEMCACHED_HOST = os.environ["MEMCACHED_HOST"]
cache_client = Client(MEMCACHED_HOST)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/healthz", response_class=PlainTextResponse)
async def health():
    return "OK"


@app.get("/api/devices", response_class=ORJSONResponse)
async def get_devices():
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

    return ORJSONResponse(devices)


@app.post("/api/devices", status_code=201, response_model=Device)
async def create_device(device: Device, db: PostgresDep):
    session, tr = db
    # To match Go implementation instead of using SQLModel factory.
    now = datetime.datetime.now()
    device.uuid = str(uuid.uuid4())
    device.created_at = now
    device.updated_at = now

    # Measure the same insert operation as in Go
    start_time = time.time()
    device_id = await session.fetchval(
        """INSERT INTO python_device (uuid, mac, firmware, created_at, updated_at) VALUES ($1, $2, $3, $4, $5) RETURNING id""",
        device.uuid,
        device.mac,
        device.firmware,
        device.created_at,
        device.updated_at,
    )
    device_out = device.model_dump()
    device_out["id"] = device_id
    await tr.commit()
    H.labels(op="insert", db="postgres").observe(time.time() - start_time)

    # Measure the same set operation as in Go
    start_time = time.time()
    # cache_client.set(device.uuid, device_out, expire=20)
    # H.labels(op="set", db="memcache").observe(time.time() - start_time)

    return ORJSONResponse(device_out)
