import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class GeneratedQuestion(Base):
    __tablename__ = "generated_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    attending_question: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    step_by_step_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    wrong_answer_analysis: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    high_yield_takeaway: Mapped[str] = mapped_column(Text, nullable=False)
    follow_up_questions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    mcq_options: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    ai_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ai_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    card: Mapped["Card"] = relationship("Card", back_populates="generated_question")
    attempts: Mapped[list["QuestionAttempt"]] = relationship(
        "QuestionAttempt", back_populates="generated_question"
    )
