import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MachineStatus(str, enum.Enum):
    running = "running"
    idle = "idle"
    maintenance = "maintenance"
    fault = "fault"


class ReadingSource(str, enum.Enum):
    simulated = "simulated"
    manual = "manual"
    csv_import = "csv_import"


class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    line: Mapped[str] = mapped_column(String(50))
    machine_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[MachineStatus] = mapped_column(
        Enum(MachineStatus), default=MachineStatus.running
    )

    readings: Mapped[list["SensorReading"]] = relationship(back_populates="machine")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id"), index=True)
    metric: Mapped[str] = mapped_column(String(50), index=True)
    value: Mapped[float]
    unit: Mapped[str] = mapped_column(String(20))
    source: Mapped[ReadingSource] = mapped_column(
        Enum(ReadingSource), default=ReadingSource.simulated
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    machine: Mapped["Machine"] = relationship(back_populates="readings")


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
    machine_id: Mapped[int | None] = mapped_column(ForeignKey("machines.id"), nullable=True)
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
