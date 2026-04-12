import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    deck_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("decks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    system_tag: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    topic_tag: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[int] = mapped_column(SmallInteger, default=2)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    deck: Mapped["Deck"] = relationship("Deck", back_populates="cards")
    generated_question: Mapped[Optional["GeneratedQuestion"]] = relationship(
        "GeneratedQuestion", back_populates="card", uselist=False
    )
    schedule_state: Mapped[Optional["ScheduleState"]] = relationship(
        "ScheduleState", back_populates="card", uselist=False
    )
