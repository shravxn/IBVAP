from datetime import datetime, timezone
from sqlalchemy import String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database.db import Base

def now(): return datetime.now(timezone.utc)

class Camera(Base):
    __tablename__ = "cameras"
    id: Mapped[int] = mapped_column(primary_key=True)
    camera_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(200), default="Demo Border Sector")
    stream_url: Mapped[str|None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="ONLINE")
    fps: Mapped[float] = mapped_column(Float, default=25)
    resolution: Mapped[str] = mapped_column(String(30), default="1920x1080")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_heartbeat: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(60), index=True)
    camera_id: Mapped[str] = mapped_column(String(50), index=True)
    object_type: Mapped[str] = mapped_column(String(50), default="Unknown")
    track_id: Mapped[str|None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    status: Mapped[str] = mapped_column(String(20), default="OPEN")
    reason: Mapped[str] = mapped_column(Text, default="Demo simulation")
    evidence_path: Mapped[str|None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    priority: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ANPRRecord(Base):
    __tablename__ = "anpr_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    plate_number: Mapped[str] = mapped_column(String(40), index=True)
    camera_id: Mapped[str] = mapped_column(String(50), index=True)
    vehicle_type: Mapped[str] = mapped_column(String(40), default="Unknown")
    ocr_confidence: Mapped[float] = mapped_column(Float, default=0)
    watchlist_status: Mapped[str] = mapped_column(String(20), default="NORMAL")
    snapshot_path: Mapped[str|None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
