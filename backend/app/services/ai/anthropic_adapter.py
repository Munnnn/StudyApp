"""Anthropic Claude adapter for the AI teaching engine."""
import json

import anthropic

from app.services.ai.base import AIGenerationError, AIService, GenerationResult, GradingResult
from app.services.ai.prompts import (
    GRADING_SYSTEM,
    GRADING_USER_TEMPLATE,
    TEACHING_SYSTEM,
    TEACHING_USER_TEMPLATE,
)

GENERATION_MODEL = "claude-haiku-4-5-20251001"
GRADING_MODEL = "claude-sonnet-4-6"


class AnthropicAdapter(AIService):
    provider_name = "anthropic"
    model_id = GENERATION_MODEL

    def __init__(self, api_key: str):
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate_teaching(self, front: str, back: str) -> GenerationResult:
        prompt = TEACHING_USER_TEMPLATE.format(front=front, back=back)
        try:
            response = await self._client.messages.create(
                model=GENERATION_MODEL,
                max_tokens=1024,
                system=[
                    {
                        "type": "text",
                        "text": TEACHING_SYSTEM,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text
            data = json.loads(raw)
            return GenerationResult(**data)
        except (json.JSONDecodeError, KeyError, Exception) as exc:
            raise AIGenerationError(f"Anthropic generate_teaching failed: {exc}") from exc

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
            response = await self._client.messages.create(
                model=GRADING_MODEL,
                max_tokens=256,
                system=[
                    {
                        "type": "text",
                        "text": GRADING_SYSTEM,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text
            data = json.loads(raw)
            return GradingResult(**data)
        except (json.JSONDecodeError, KeyError, Exception) as exc:
            raise AIGenerationError(f"Anthropic grade_typed_answer failed: {exc}") from exc
