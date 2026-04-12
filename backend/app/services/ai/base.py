"""Abstract AI service interface."""
from abc import ABC, abstractmethod

from pydantic import BaseModel


class GenerationResult(BaseModel):
    attending_question: str
    correct_answer: str
    step_by_step_explanation: str
    wrong_answer_analysis: list[str]
    high_yield_takeaway: str
    follow_up_questions: list[str]
    mcq_options: list[str]  # index 0 is always the correct answer


class GradingResult(BaseModel):
    score: int          # 0-4
    justification: str


class AIGenerationError(Exception):
    pass


class AIService(ABC):
    provider_name: str
    model_id: str

    @abstractmethod
    async def generate_teaching(self, front: str, back: str) -> GenerationResult:
        """Transform a flashcard front/back into a full teaching interaction."""
        ...

    @abstractmethod
    async def grade_typed_answer(
        self,
        question: str,
        correct_answer: str,
        user_answer: str,
    ) -> GradingResult:
        """Grade a student's free-typed answer on a 0-4 scale."""
        ...
