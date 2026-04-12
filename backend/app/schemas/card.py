import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CardCreate(BaseModel):
    front: str
    back: str
    system_tag: Optional[str] = None
    topic_tag: Optional[str] = None
    difficulty: int = Field(default=2, ge=1, le=5)


class CardUpdate(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None
    system_tag: Optional[str] = None
    topic_tag: Optional[str] = None
    difficulty: Optional[int] = Field(default=None, ge=1, le=5)


class CardOut(BaseModel):
    id: uuid.UUID
    deck_id: uuid.UUID
    front: str
    back: str
    system_tag: Optional[str]
    topic_tag: Optional[str]
    difficulty: int
    created_at: datetime

    model_config = {"from_attributes": True}
