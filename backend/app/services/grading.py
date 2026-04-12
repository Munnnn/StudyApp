"""Wrapper that calls the AI service to grade a typed answer."""
from app.services.ai.base import AIService, GradingResult


async def score_typed_answer(
    question: str,
    correct_answer: str,
    user_answer: str,
    ai: AIService,
) -> GradingResult:
    if not user_answer or not user_answer.strip():
        return GradingResult(score=0, justification="No answer provided.")
    return await ai.grade_typed_answer(
        question=question,
        correct_answer=correct_answer,
        user_answer=user_answer,
    )
