import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DeviceStatus(str, enum.Enum):
    online = "online"
    idle = "idle"
    updating = "updating"
    fault = "fault"


class ReadingSource(str, enum.Enum):
    simulated = "simulated"
    manual = "manual"
    csv_import = "csv_import"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    bench: Mapped[str] = mapped_column(String(50))
    device_type: Mapped[str] = mapped_column(String(50))
    firmware_version: Mapped[str] = mapped_column(String(20), default="v0.0.0")
    status: Mapped[DeviceStatus] = mapped_column(
        Enum(DeviceStatus), default=DeviceStatus.online
    )

    readings: Mapped[list["SensorReading"]] = relationship(back_populates="device")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True)
    metric: Mapped[str] = mapped_column(String(50), index=True)
    value: Mapped[float]
    unit: Mapped[str] = mapped_column(String(20))
    source: Mapped[ReadingSource] = mapped_column(
        Enum(ReadingSource), default=ReadingSource.simulated
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    device: Mapped["Device"] = relationship(back_populates="readings")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))
    quantity: Mapped[int] = mapped_column(default=0)
    min_quantity: Mapped[int] = mapped_column(default=0)
    location: Mapped[str] = mapped_column(String(100), default="")
    unit_cost: Mapped[float] = mapped_column(default=0.0)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id"), nullable=True)
    metric: Mapped[str] = mapped_column(String(50), default="")
    severity: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(255))
    acknowledged: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="viewer")
