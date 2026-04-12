"""
Lazy, idempotent card-to-question generation.
Uses a PostgreSQL advisory lock keyed on the card UUID to prevent
duplicate generation under concurrent requests.
"""
import uuid

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card import Card
from app.models.generated_question import GeneratedQuestion
from app.services.ai.base import AIService, AIGenerationError


async def generate_for_card(
    card: Card,
    db: AsyncSession,
    ai: AIService,
) -> GeneratedQuestion:
    """
    Return the GeneratedQuestion for `card`, creating it if absent.
    Thread-safe: uses pg_try_advisory_xact_lock to prevent double-generation.
    Never accesses ORM lazy relationships — always queries directly.
    """
    # Check for existing — always query directly (no lazy-load in async)
    result = await db.execute(
        select(GeneratedQuestion).where(GeneratedQuestion.card_id == card.id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    # Acquire advisory lock (auto-released at transaction end)
    lock_key = _uuid_to_lock_key(card.id)
    lock_result = await db.execute(text(f"SELECT pg_try_advisory_xact_lock({lock_key})"))
    got_lock = lock_result.scalar_one()

    if not got_lock:
        # Another request is generating; wait briefly and re-read
        import asyncio
        await asyncio.sleep(0.5)
        result2 = await db.execute(
            select(GeneratedQuestion).where(GeneratedQuestion.card_id == card.id)
        )
        gq = result2.scalar_one_or_none()
        if gq:
            return gq
        raise AIGenerationError("Could not acquire generation lock — please retry")

    # Double-check after acquiring lock
    result3 = await db.execute(
        select(GeneratedQuestion).where(GeneratedQuestion.card_id == card.id)
    )
    existing2 = result3.scalar_one_or_none()
    if existing2:
        return existing2

    gen = await ai.generate_teaching(front=card.front, back=card.back)

    gq = GeneratedQuestion(
        card_id=card.id,
        attending_question=gen.attending_question,
        correct_answer=gen.correct_answer,
        step_by_step_explanation=gen.step_by_step_explanation,
        wrong_answer_analysis=gen.wrong_answer_analysis,
        high_yield_takeaway=gen.high_yield_takeaway,
        follow_up_questions=gen.follow_up_questions,
        mcq_options=gen.mcq_options,
        ai_provider=ai.provider_name,
        ai_model=ai.model_id,
    )
    db.add(gq)
    await db.commit()
    await db.refresh(gq)
    return gq


def _uuid_to_lock_key(uid: uuid.UUID) -> int:
    """Convert UUID to a 64-bit signed integer for pg_advisory_lock."""
    val = uid.int
    # Take lower 64 bits and convert to signed
    key = val & 0xFFFFFFFFFFFFFFFF
    if key >= (1 << 63):
        key -= (1 << 64)
    return key
