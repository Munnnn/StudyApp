import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.deck import SourceType


class DeckCreate(BaseModel):
    title: str
    description: Optional[str] = None
    source_type: SourceType = SourceType.manual


class DeckUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class DeckOut(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    title: str
    description: Optional[str]
    source_type: SourceType
    created_at: datetime
    card_count: int = 0

    model_config = {"from_attributes": True}
