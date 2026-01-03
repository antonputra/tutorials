import datetime
import logging
from uuid6 import uuid7

from asyncpg import PostgresError
from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse, PlainTextResponse
from pydantic import BaseModel

from db import PostgresDep, lifespan

app = FastAPI(lifespan=lifespan)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

INSERT_QUERY = """
INSERT INTO fastapi_app (name, address, phone, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5)
RETURNING id;
"""


@app.get("/healthz", response_class=PlainTextResponse)
async def health():
    return "OK"


@app.get("/api/devices", response_class=ORJSONResponse)
async def get_devices():
    devices = (
        {
            "uuid": uuid7(),
            "mac": "5F-33-CC-1F-43-82",
            "firmware": "2.1.6",
        },
        {
            "uuid": uuid7(),
            "mac": "EF-2B-C4-F5-D6-34",
            "firmware": "2.1.5",
        },
        {
            "uuid": uuid7(),
            "mac": "62-46-13-B7-B3-A1",
            "firmware": "3.0.0",
        },
    )

    return devices


class UserRequest(BaseModel):
    name: str
    address: str
    phone: str


@app.post("/api/users", status_code=201, response_class=ORJSONResponse)
async def create_user(user: UserRequest, conn: PostgresDep):
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        row = await conn.fetchrow(
            INSERT_QUERY, user.name, user.address, user.phone, now, now
        )

        if not row:
            raise HTTPException(status_code=500, detail="Failed to create user record")

        return {
            "id": row["id"],
            "name": user.name,
            "address": user.address,
            "phone": user.phone,
            "created_at": now,
            "updated_at": now,
        }

    except PostgresError:
        logger.exception("Postgres error", extra={"user_data": user.model_dump()})
        raise HTTPException(
            status_code=500, detail="Database error occurred while creating user"
        )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Unhandled exception")
    return ORJSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
