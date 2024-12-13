import datetime

from pydantic import BaseModel


class Device(BaseModel):
    id: int | None = None
    uuid: str | None = None
    mac: str | None = None
    firmware: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
