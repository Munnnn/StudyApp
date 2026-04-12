import uuid
import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, SmallInteger, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class MasteryLevel(str, enum.Enum):
    weak = "weak"
    fragile = "fragile"
    developing = "developing"
    strong = "strong"


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    generated_question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("generated_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    typed_answer_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    typed_answer_score: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    mcq_selected_index: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    mcq_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    response_time_text_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_time_mcq_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mastery_level: Mapped[Optional[MasteryLevel]] = mapped_column(
        Enum(MasteryLevel, name="mastery_level_enum"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="attempts")
    generated_question: Mapped["GeneratedQuestion"] = relationship(
        "GeneratedQuestion", back_populates="attempts"
    )
