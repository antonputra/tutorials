import datetime

from sqlmodel import Field, SQLModel


class Device(SQLModel, table=True):
    __tablename__: str = "python_device"

    id: int | None = Field(default=None, primary_key=True)
    uuid: str | None = Field(default=None, max_length=255)
    mac: str | None = Field(default=None, max_length=255)
    firmware: str | None = Field(default=None, max_length=255)
    created_at: datetime.datetime
    updated_at: datetime.datetime

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
