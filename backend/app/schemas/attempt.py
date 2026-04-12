import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.attempt import MasteryLevel


class AttemptOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    generated_question_id: uuid.UUID
    typed_answer_raw: Optional[str]
    typed_answer_score: Optional[int]
    mcq_selected_index: Optional[int]
    mcq_correct: Optional[bool]
    mastery_level: Optional[MasteryLevel]
    created_at: datetime

    model_config = {"from_attributes": True}
