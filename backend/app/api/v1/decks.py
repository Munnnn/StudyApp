import io
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user
from app.models.card import Card
from app.models.deck import Deck, SourceType
from app.models.schedule_state import ScheduleState
from app.models.user import User
from app.schemas.card import CardOut
from app.schemas.deck import DeckCreate, DeckOut, DeckUpdate
from app.services.csv_import import parse_csv

router = APIRouter()


async def _deck_or_404(deck_id: uuid.UUID, user: User, db: AsyncSession) -> Deck:
    result = await db.execute(
        select(Deck).where(Deck.id == deck_id, Deck.owner_id == user.id)
    )
    deck = result.scalar_one_or_none()
    if deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck


async def _card_count(deck_id: uuid.UUID, db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count()).where(Card.deck_id == deck_id)
    )
    return result.scalar_one()


@router.get("", response_model=list[DeckOut])
async def list_decks(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deck).where(Deck.owner_id == user.id).order_by(Deck.created_at.desc()))
    decks = result.scalars().all()
    out = []
    for d in decks:
        count = await _card_count(d.id, db)
        out.append(DeckOut(
            id=d.id, owner_id=d.owner_id, title=d.title,
            description=d.description, source_type=d.source_type,
            created_at=d.created_at, card_count=count
        ))
    return out


@router.post("", response_model=DeckOut, status_code=201)
async def create_deck(
    body: DeckCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deck = Deck(owner_id=user.id, **body.model_dump())
    db.add(deck)
    await db.commit()
    await db.refresh(deck)
    return DeckOut(**deck.__dict__, card_count=0)


@router.get("/{deck_id}", response_model=DeckOut)
async def get_deck(
    deck_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deck = await _deck_or_404(deck_id, user, db)
    count = await _card_count(deck_id, db)
    return DeckOut(**deck.__dict__, card_count=count)


@router.patch("/{deck_id}", response_model=DeckOut)
async def update_deck(
    deck_id: uuid.UUID,
    body: DeckUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deck = await _deck_or_404(deck_id, user, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(deck, field, value)
    await db.commit()
    await db.refresh(deck)
    count = await _card_count(deck_id, db)
    return DeckOut(**deck.__dict__, card_count=count)


@router.delete("/{deck_id}", status_code=204)
async def delete_deck(
    deck_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deck = await _deck_or_404(deck_id, user, db)
    await db.delete(deck)
    await db.commit()


@router.get("/{deck_id}/cards", response_model=list[CardOut])
async def list_cards(
    deck_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _deck_or_404(deck_id, user, db)
    result = await db.execute(select(Card).where(Card.deck_id == deck_id).order_by(Card.created_at))
    return result.scalars().all()


@router.post("/{deck_id}/cards", response_model=CardOut, status_code=201)
async def add_card(
    deck_id: uuid.UUID,
    body: "CardCreateBody",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.schemas.card import CardCreate
    await _deck_or_404(deck_id, user, db)
    card = Card(deck_id=deck_id, **body.model_dump())
    db.add(card)
    await db.commit()
    await db.refresh(card)
    # Initialize schedule state so it surfaces immediately
    from datetime import datetime, timezone
    ss = ScheduleState(
        user_id=user.id,
        card_id=card.id,
        next_due_at=datetime.now(timezone.utc),
        interval_min=10,
    )
    db.add(ss)
    await db.commit()
    return card


# workaround: reuse CardCreate
from app.schemas.card import CardCreate as CardCreateBody  # noqa: E402


@router.post("/{deck_id}/import-csv", status_code=201)
async def import_csv(
    deck_id: uuid.UUID,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    deck = await _deck_or_404(deck_id, user, db)
    content = await file.read()
    try:
        card_creates = parse_csv(content.decode("utf-8-sig"))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"CSV parse error: {exc}")

    from datetime import datetime, timezone
    cards = []
    for cc in card_creates:
        card = Card(deck_id=deck_id, **cc.model_dump())
        db.add(card)
        cards.append(card)

    deck.source_type = SourceType.csv
    await db.commit()
    for card in cards:
        await db.refresh(card)
        ss = ScheduleState(
            user_id=user.id,
            card_id=card.id,
            next_due_at=datetime.now(timezone.utc),
            interval_min=10,
        )
        db.add(ss)
    await db.commit()

    return {"imported": len(cards)}
