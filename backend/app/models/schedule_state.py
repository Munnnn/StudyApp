import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.attempt import MasteryLevel


class ScheduleState(Base):
    __tablename__ = "schedule_state"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True
    )
    next_due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    interval_min: Mapped[int] = mapped_column(Integer, default=10)
    last_mastery: Mapped[MasteryLevel] = mapped_column(
        Enum(MasteryLevel, name="mastery_level_enum"), default=MasteryLevel.weak
    )
    consecutive_strong: Mapped[int] = mapped_column(Integer, default=0)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User"] = relationship("User", back_populates="schedule_states")
    card: Mapped["Card"] = relationship("Card", back_populates="schedule_state")
