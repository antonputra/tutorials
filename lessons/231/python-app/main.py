import uuid
import time
import datetime
import logging
import os

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from models import Device
from db import PostgresDep
from metrics import H
from prometheus_client import make_asgi_app
from pymemcache.client.base import Client

app = FastAPI()

MEMCACHED_HOST = os.environ['MEMCACHED_HOST']
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
async def health():
    return "OK"


@app.get("/api/devices")
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
        }
    ]

    return devices


@app.post("/api/devices", status_code=201)
async def create_device(device: Device, session: PostgresDep) -> Device:
    # To match Go implementation instead of using SQLModel factory.
    now = datetime.datetime.now(datetime.timezone.utc)
    device.uuid = str(uuid.uuid4())
    device.created_at = now
    device.updated_at = now

    # Measure the same insert operation as in Go
    start_time = time.time()
    session.add(device)
    session.commit()
    H.labels(op="insert", db="postgres").observe(time.time() - start_time)

    # Measure the same set operation as in Go
    start_time = time.time()
    cache_client.set(device.uuid, device.as_dict(), expire=20)
    H.labels(op="set", db="memcache").observe(time.time() - start_time)

    # Refresh the device to return it to the client.
    session.refresh(device)

    return device
