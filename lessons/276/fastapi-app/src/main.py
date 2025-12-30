import datetime
import logging
from uuid6 import uuid7

from asyncpg import PostgresError
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import ORJSONResponse, PlainTextResponse

from db import PostgresDep, lifespan

app = FastAPI(lifespan=lifespan)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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


@app.post("/api/users", status_code=201, response_class=ORJSONResponse)
async def create_user(request: Request, conn: PostgresDep):
    data = await request.json()
    try:
        name = data["name"]
        address = data["address"]
        phone = data["phone"]

    except KeyError:
        logger.exception("Missing input")
        raise HTTPException(status_code=422, detail="Incomplete payload: name / address / phone missing")

    try:
        now = datetime.datetime.now(datetime.timezone.utc)

        insert_query = """
            INSERT INTO fastapi_app (name, address, phone, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id;
            """

        row = await conn.fetchrow(insert_query, name, address, phone, now, now)

        if not row:
            raise HTTPException(status_code=500, detail="Failed to create user record")

        user_dict = {
            "id": row["id"],
            "name": name,
            "address": address,
            "phone": phone,
            "created_at": now,
            "updated_at": now,
        }

        return user_dict

    except PostgresError:
        logger.exception("Postgres error")
        raise HTTPException(
            status_code=500, detail="Database error occurred while creating user"
        )

    except Exception:
        logger.exception("Unknown error")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred while creating user"
        )
