import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    device_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notification_interval_min: Mapped[int] = mapped_column(Integer, default=30)
    quiet_hours_start: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # "HH:MM"
    quiet_hours_end: Mapped[Optional[str]] = mapped_column(String, nullable=True)   # "HH:MM"
    paused: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    decks: Mapped[list["Deck"]] = relationship("Deck", back_populates="owner", cascade="all, delete-orphan")
    attempts: Mapped[list["QuestionAttempt"]] = relationship("QuestionAttempt", back_populates="user")
    schedule_states: Mapped[list["ScheduleState"]] = relationship("ScheduleState", back_populates="user")
