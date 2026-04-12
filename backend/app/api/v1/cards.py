import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user
from app.models.card import Card
from app.models.deck import Deck
from app.models.generated_question import GeneratedQuestion
from app.models.user import User
from app.schemas.card import CardOut, CardUpdate

router = APIRouter()


async def _card_owned_or_404(card_id: uuid.UUID, user: User, db: AsyncSession) -> Card:
    result = await db.execute(
        select(Card).join(Deck, Card.deck_id == Deck.id).where(
            Card.id == card_id, Deck.owner_id == user.id
        )
    )
    card = result.scalar_one_or_none()
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.patch("/{card_id}", response_model=CardOut)
async def update_card(
    card_id: uuid.UUID,
    body: CardUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    card = await _card_owned_or_404(card_id, user, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(card, field, value)
    # Invalidate generated question so it regenerates with new content
    gq_result = await db.execute(select(GeneratedQuestion).where(GeneratedQuestion.card_id == card.id))
    existing_gq = gq_result.scalar_one_or_none()
    if existing_gq:
        await db.delete(existing_gq)
    await db.commit()
    await db.refresh(card)
    return card


@router.delete("/{card_id}", status_code=204)
async def delete_card(
    card_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    card = await _card_owned_or_404(card_id, user, db)
    await db.delete(card)
    await db.commit()
