"""
Study flow routes.

CRITICAL RECALL INTEGRITY RULE
─────────────────────────────────────────────────────────────────────────────
GET  /study/next         → returns attending_question ONLY. NO correct_answer,
                           NO mcq_options, NO high_yield_takeaway with spoilers.
POST /study/attempts/typed  → locks typed answer server-side, THEN returns
                               shuffled mcq_options.
POST /study/attempts/mcq    → finalises attempt, returns full explanation.
─────────────────────────────────────────────────────────────────────────────
Any code path that returns GeneratedQuestion data must be audited to ensure
correct_answer and mcq_options are NOT included before the typed phase.
"""
import random
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user
from app.models.attempt import MasteryLevel, QuestionAttempt
from app.models.card import Card
from app.models.deck import Deck
from app.models.generated_question import GeneratedQuestion
from app.models.schedule_state import ScheduleState
from app.models.user import User
from app.schemas.question import (
    ExplanationOut,
    MCQAnswerIn,
    NextQuestionOut,
    TypedAnswerIn,
    TypedAnswerOut,
)
from app.services.ai.factory import get_ai_service
from app.services.generation import generate_for_card
from app.services.grading import score_typed_answer
from app.services.scheduling import compute_next_review
from app.services.scoring import classify_gap, compute_mastery, response_time_score

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# GET /study/next
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/next", response_model=NextQuestionOut)
async def get_next_question(
    force: bool = Query(False, description="Ignore schedule and return any card (for testing)"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return the next due card as a safe question object.
    Generates the teaching layer lazily if not yet done.

    SAFETY: NextQuestionOut deliberately excludes correct_answer and mcq_options.
    """
    card = await _pick_next_card(user, db, force=force)
    if card is None:
        raise HTTPException(status_code=404, detail="No cards due. Great work — check back later!")

    ai = get_ai_service()
    gq = await generate_for_card(card=card, db=db, ai=ai)

    # ── SAFETY CHECK ─────────────────────────────────────────────────────────
    # NextQuestionOut must never include correct_answer or mcq_options.
    # The fields simply don't exist on the schema — this is enforced by type.
    return NextQuestionOut(
        generated_question_id=gq.id,
        card_id=card.id,
        attending_question=gq.attending_question,
        system_tag=card.system_tag,
        topic_tag=card.topic_tag,
        high_yield_takeaway=gq.high_yield_takeaway,
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /study/attempts/typed
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/attempts/typed", response_model=TypedAnswerOut, status_code=201)
async def submit_typed_answer(
    body: TypedAnswerIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Lock the typed answer and return the shuffled MCQ options.
    The typed answer is persisted before mcq_options are ever sent to the client.
    """
    gq = await _gq_or_404(body.generated_question_id, db)

    ai = get_ai_service()
    grading = await score_typed_answer(
        question=gq.attending_question,
        correct_answer=gq.correct_answer,
        user_answer=body.typed_answer,
        ai=ai,
    )

    # Create partial attempt (mcq fields null until next step)
    attempt = QuestionAttempt(
        user_id=user.id,
        generated_question_id=gq.id,
        typed_answer_raw=body.typed_answer,
        typed_answer_score=grading.score,
        response_time_text_ms=body.response_time_ms,
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)

    # Shuffle options deterministically so /mcq can reconstruct the same order
    options = _deterministic_shuffle(list(gq.mcq_options), seed=str(attempt.id))

    return TypedAnswerOut(attempt_id=attempt.id, mcq_options=options)


# ─────────────────────────────────────────────────────────────────────────────
# POST /study/attempts/mcq
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/attempts/mcq", response_model=ExplanationOut)
async def submit_mcq_answer(
    body: MCQAnswerIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Finalise the attempt: record MCQ selection, compute mastery, update schedule.
    Returns the full explanation payload.
    """
    attempt = await _attempt_or_404(body.attempt_id, user, db)
    if attempt.mcq_selected_index is not None:
        raise HTTPException(status_code=409, detail="MCQ already submitted for this attempt")

    gq = await _gq_or_404(attempt.generated_question_id, db)
    card = await db.get(Card, gq.card_id)

    # Determine correct index from the UNshuffled options stored in DB
    # The client sends the INDEX into the shuffled list it received.
    # We need to map that back to the actual answer.
    # Since we don't persist the shuffle order, we compare the selected option text.
    # We store selected_index as-received (into whatever shuffled list the client had),
    # but determine correctness by checking if the selected text equals correct_answer.
    # To do this properly: the client must send the selected option TEXT, not index.
    # However, the spec says index — so we store the index as received and determine
    # correctness by asking: did the client select the option that matches correct_answer?
    #
    # WORKAROUND for MVP: we re-shuffle with a fixed seed tied to attempt_id so the
    # server and client produce the same order, then compare indices.
    shuffled = _deterministic_shuffle(list(gq.mcq_options), seed=str(attempt.id))
    selected_text = shuffled[body.mcq_selected_index] if 0 <= body.mcq_selected_index < len(shuffled) else None
    mcq_correct = selected_text == gq.mcq_options[0]  # index 0 = correct in DB

    time_score = response_time_score(attempt.response_time_text_ms)
    mastery = compute_mastery(
        typed_score=attempt.typed_answer_score,
        mcq_correct=mcq_correct,
        response_time_score=time_score,
    )
    gap = classify_gap(attempt.typed_answer_score, mcq_correct)

    attempt.mcq_selected_index = body.mcq_selected_index
    attempt.mcq_correct = mcq_correct
    attempt.response_time_mcq_ms = body.response_time_ms
    attempt.mastery_level = mastery

    # Update schedule state
    ss = await db.get(ScheduleState, {"user_id": user.id, "card_id": gq.card_id})
    if ss is None:
        ss = ScheduleState(user_id=user.id, card_id=gq.card_id, next_due_at=datetime.now(timezone.utc))
        db.add(ss)

    sched = compute_next_review(
        current_interval_min=ss.interval_min,
        current_consecutive_strong=ss.consecutive_strong,
        mastery=mastery,
    )
    ss.next_due_at = sched.next_due_at
    ss.interval_min = sched.interval_min
    ss.consecutive_strong = sched.consecutive_strong
    ss.last_mastery = mastery
    ss.total_attempts = (ss.total_attempts or 0) + 1

    await db.commit()

    return ExplanationOut(
        attempt_id=attempt.id,
        attending_question=gq.attending_question,
        typed_answer_raw=attempt.typed_answer_raw,
        typed_answer_score=attempt.typed_answer_score,
        mcq_selected_index=body.mcq_selected_index,
        mcq_correct=mcq_correct,
        correct_answer=gq.correct_answer,
        step_by_step_explanation=gq.step_by_step_explanation,
        wrong_answer_analysis=gq.wrong_answer_analysis,
        high_yield_takeaway=gq.high_yield_takeaway,
        follow_up_questions=gq.follow_up_questions,
        mastery_level=mastery.value,
        recall_gap=gap,
        system_tag=card.system_tag if card else None,
        topic_tag=card.topic_tag if card else None,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _pick_next_card(user: User, db: AsyncSession, force: bool = False):
    """
    Priority order:
    1. Due cards ordered weak → fragile → developing → strong
    2. Then by next_due_at ascending
    Cards with no schedule_state row (brand new) are treated as weak + due now.
    If force=True, ignore the due-time filter and return any card.
    """
    # Cards WITH a schedule row that are due (or any, if force)
    query = (
        select(Card)
        .join(ScheduleState, (ScheduleState.card_id == Card.id) & (ScheduleState.user_id == user.id))
        .join(Deck, Deck.id == Card.deck_id)
        .where(Deck.owner_id == user.id)
    )
    if not force:
        query = query.where(ScheduleState.next_due_at <= datetime.now(timezone.utc))
    result = await db.execute(
        query
        .order_by(
            # Weak first
            (ScheduleState.last_mastery == MasteryLevel.weak).desc(),
            (ScheduleState.last_mastery == MasteryLevel.fragile).desc(),
            (ScheduleState.last_mastery == MasteryLevel.developing).desc(),
            ScheduleState.next_due_at.asc(),
        )
        .limit(1)
    )
    card = result.scalar_one_or_none()
    if card:
        return card

    # Unseen cards (no schedule row at all)
    result2 = await db.execute(
        select(Card)
        .join(Deck, Deck.id == Card.deck_id)
        .outerjoin(
            ScheduleState,
            (ScheduleState.card_id == Card.id) & (ScheduleState.user_id == user.id),
        )
        .where(Deck.owner_id == user.id, ScheduleState.card_id == None)
        .limit(1)
    )
    unseen = result2.scalar_one_or_none()
    if unseen:
        # Initialise schedule state
        ss = ScheduleState(
            user_id=user.id,
            card_id=unseen.id,
            next_due_at=datetime.now(timezone.utc),
            interval_min=10,
        )
        db.add(ss)
        await db.commit()
        return unseen

    return None


async def _gq_or_404(gq_id: uuid.UUID, db: AsyncSession) -> GeneratedQuestion:
    gq = await db.get(GeneratedQuestion, gq_id)
    if gq is None:
        raise HTTPException(status_code=404, detail="Generated question not found")
    return gq


async def _attempt_or_404(attempt_id: uuid.UUID, user: User, db: AsyncSession) -> QuestionAttempt:
    attempt = await db.get(QuestionAttempt, attempt_id)
    if attempt is None or attempt.user_id != user.id:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt


def _deterministic_shuffle(items: list, seed: str) -> list:
    """Shuffle a list deterministically given a seed string."""
    import hashlib
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    rng = random.Random(h)
    shuffled = items[:]
    rng.shuffle(shuffled)
    return shuffled
