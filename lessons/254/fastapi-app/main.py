import logging

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, PlainTextResponse


app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@app.get("/healthz", response_class=PlainTextResponse)
async def health():
    return "OK"


@app.get("/api/devices", response_class=ORJSONResponse)
async def get_devices():
    devices = (
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
    )

    return devices
