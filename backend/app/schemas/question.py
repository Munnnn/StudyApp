import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NextQuestionOut(BaseModel):
    """Safe payload for /study/next — never includes correct_answer or mcq_options."""
    generated_question_id: uuid.UUID
    card_id: uuid.UUID
    attending_question: str
    system_tag: Optional[str]
    topic_tag: Optional[str]
    high_yield_takeaway: str


class TypedAnswerIn(BaseModel):
    generated_question_id: uuid.UUID
    typed_answer: str
    response_time_ms: Optional[int] = None


class TypedAnswerOut(BaseModel):
    """Returned after locking the typed answer. Now reveals MCQ options."""
    attempt_id: uuid.UUID
    mcq_options: list[str]  # shuffled; client does NOT know which index is correct


class MCQAnswerIn(BaseModel):
    attempt_id: uuid.UUID
    mcq_selected_index: int
    response_time_ms: Optional[int] = None


class ExplanationOut(BaseModel):
    """Full teaching payload returned after MCQ submission."""
    attempt_id: uuid.UUID
    attending_question: str
    typed_answer_raw: str
    typed_answer_score: int
    mcq_selected_index: int
    mcq_correct: bool
    correct_answer: str
    step_by_step_explanation: str
    wrong_answer_analysis: list[str]
    high_yield_takeaway: str
    follow_up_questions: list[str]
    mastery_level: str
    recall_gap: str  # "both" | "recognition_only" | "recall_only" | "neither"
    system_tag: Optional[str]
    topic_tag: Optional[str]
