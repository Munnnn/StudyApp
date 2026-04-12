from fastapi import APIRouter, Depends
from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user
from app.models.attempt import MasteryLevel, QuestionAttempt
from app.models.card import Card
from app.models.deck import Deck
from app.models.generated_question import GeneratedQuestion
from app.models.schedule_state import ScheduleState
from app.models.user import User
from app.schemas.dashboard import DashboardOut, MasteryDistribution, SystemStat

router = APIRouter()


@router.get("", response_model=DashboardOut)
async def get_dashboard(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Total attempts
    total_q = await db.execute(
        select(func.count()).where(QuestionAttempt.user_id == user.id)
    )
    total = total_q.scalar_one()

    # Mastery distribution (only finalized attempts)
    dist = MasteryDistribution()
    for level in MasteryLevel:
        cnt_q = await db.execute(
            select(func.count()).where(
                QuestionAttempt.user_id == user.id,
                QuestionAttempt.mastery_level == level,
            )
        )
        setattr(dist, level.value, cnt_q.scalar_one())

    # Recognition-only (typed wrong ≤1, MCQ correct)
    recog_q = await db.execute(
        select(func.count()).where(
            QuestionAttempt.user_id == user.id,
            QuestionAttempt.typed_answer_score <= 1,
            QuestionAttempt.mcq_correct == True,
        )
    )
    recognition_only = recog_q.scalar_one()

    # Strong mastery
    strong_q = await db.execute(
        select(func.count()).where(
            QuestionAttempt.user_id == user.id,
            QuestionAttempt.mastery_level == MasteryLevel.strong,
        )
    )
    strong_count = strong_q.scalar_one()

    # Cards studied vs total
    studied_q = await db.execute(
        select(func.count(func.distinct(QuestionAttempt.generated_question_id))).where(
            QuestionAttempt.user_id == user.id
        )
    )
    cards_studied = studied_q.scalar_one()

    total_cards_q = await db.execute(
        select(func.count()).select_from(Card).join(Deck).where(Deck.owner_id == user.id)
    )
    cards_total = total_cards_q.scalar_one()

    # Weakest systems
    system_rows = await db.execute(
        select(
            Card.system_tag,
            func.count(QuestionAttempt.id).label("total"),
            func.avg(QuestionAttempt.typed_answer_score).label("avg_score"),
            func.sum(
                (QuestionAttempt.typed_answer_score <= 1).cast(Integer) *
                QuestionAttempt.mcq_correct.cast(Integer)
            ).label("gap"),
        )
        .join(GeneratedQuestion, GeneratedQuestion.id == QuestionAttempt.generated_question_id)
        .join(Card, Card.id == GeneratedQuestion.card_id)
        .where(QuestionAttempt.user_id == user.id, Card.system_tag != None)
        .group_by(Card.system_tag)
        .order_by(func.avg(QuestionAttempt.typed_answer_score).asc())
        .limit(5)
    )
    weakest_systems = [
        SystemStat(
            system_tag=row.system_tag,
            total_attempts=row.total,
            avg_typed_score=float(row.avg_score or 0),
            recall_gap_count=int(row.gap or 0),
        )
        for row in system_rows
    ]

    # Weakest topics (lowest avg typed score)
    topic_rows = await db.execute(
        select(Card.topic_tag, func.avg(QuestionAttempt.typed_answer_score).label("avg"))
        .join(GeneratedQuestion, GeneratedQuestion.id == QuestionAttempt.generated_question_id)
        .join(Card, Card.id == GeneratedQuestion.card_id)
        .where(QuestionAttempt.user_id == user.id, Card.topic_tag != None)
        .group_by(Card.topic_tag)
        .order_by(func.avg(QuestionAttempt.typed_answer_score).asc())
        .limit(5)
    )
    weakest_topics = [row.topic_tag for row in topic_rows]

    return DashboardOut(
        total_attempts=total,
        mastery_distribution=dist,
        weakest_systems=weakest_systems,
        weakest_topics=weakest_topics,
        recognition_only_count=recognition_only,
        strong_mastery_count=strong_count,
        cards_studied=cards_studied,
        cards_total=cards_total,
    )
