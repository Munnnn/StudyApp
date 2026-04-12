"""OpenAI adapter for the AI teaching engine."""
import json

from openai import AsyncOpenAI

from app.services.ai.base import AIGenerationError, AIService, GenerationResult, GradingResult
from app.services.ai.prompts import (
    GRADING_SYSTEM,
    GRADING_USER_TEMPLATE,
    TEACHING_SYSTEM,
    TEACHING_USER_TEMPLATE,
)

GENERATION_MODEL = "gpt-4o-mini"
GRADING_MODEL = "gpt-4o"


class OpenAIAdapter(AIService):
    provider_name = "openai"
    model_id = GENERATION_MODEL

    def __init__(self, api_key: str):
        self._client = AsyncOpenAI(api_key=api_key)

    async def generate_teaching(self, front: str, back: str) -> GenerationResult:
        prompt = TEACHING_USER_TEMPLATE.format(front=front, back=back)
        try:
            response = await self._client.chat.completions.create(
                model=GENERATION_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": TEACHING_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1024,
            )
            raw = response.choices[0].message.content
            data = json.loads(raw)
            return GenerationResult(**data)
        except (json.JSONDecodeError, KeyError, Exception) as exc:
            raise AIGenerationError(f"OpenAI generate_teaching failed: {exc}") from exc

    async def grade_typed_answer(
        self,
        question: str,
        correct_answer: str,
        user_answer: str,
    ) -> GradingResult:
        prompt = GRADING_USER_TEMPLATE.format(
            question=question, correct=correct_answer, user_answer=user_answer
        )
        try:
            response = await self._client.chat.completions.create(
                model=GRADING_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": GRADING_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=256,
            )
            raw = response.choices[0].message.content
            data = json.loads(raw)
            return GradingResult(**data)
        except (json.JSONDecodeError, KeyError, Exception) as exc:
            raise AIGenerationError(f"OpenAI grade_typed_answer failed: {exc}") from exc
