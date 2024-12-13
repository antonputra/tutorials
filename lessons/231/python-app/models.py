import datetime
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text, Time, func, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class Device(Base):
    __tablename__ = "python_device"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )
    uuid: Mapped[Optional[UUID]] = mapped_column(
        PostgresUUID(as_uuid=True), default=None
    )
    mac: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    firmware: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), server_onupdate=func.now()
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
