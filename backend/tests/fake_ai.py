"""Deterministic AI service for tests — no network calls."""
from app.services.ai.base import AIService, GenerationResult, GradingResult


FAKE_RESULT = GenerationResult(
    attending_question="What is the most likely cause of hypercalcemia with low PTH?",
    correct_answer="Malignancy (PTHrP secretion)",
    step_by_step_explanation=(
        "PTHrP mimics PTH at the receptor, driving hypercalcemia while suppressing "
        "endogenous PTH via negative feedback. Malignancy is the most common cause "
        "of hypercalcemia with low PTH."
    ),
    wrong_answer_analysis=[
        "Primary hyperparathyroidism: PTH would be HIGH, not low.",
        "Vitamin D toxicity: PTH is suppressed but not from PTHrP; check 25-OH-D.",
        "Familial hypocalciuric hypercalcemia: PTH normal-to-high, benign.",
    ],
    high_yield_takeaway="Hypercalcemia + low PTH → think malignancy (PTHrP) first.",
    follow_up_questions=[
        "Which malignancies most commonly secrete PTHrP?",
        "How do you differentiate PTHrP-mediated hypercalcemia from 1,25-D excess in lymphoma?",
    ],
    mcq_options=[
        "Malignancy (PTHrP)",
        "Primary hyperparathyroidism",
        "Vitamin D toxicity",
        "Familial hypocalciuric hypercalcemia",
    ],
)


class FakeAIService(AIService):
    provider_name = "fake"
    model_id = "fake-v1"

    def __init__(self, typed_score: int = 4):
        self._typed_score = typed_score

    async def generate_teaching(self, front: str, back: str) -> GenerationResult:
        return FAKE_RESULT

    async def grade_typed_answer(
        self,
        question: str,
        correct_answer: str,
        user_answer: str,
    ) -> GradingResult:
        if not user_answer or not user_answer.strip():
            return GradingResult(score=0, justification="Blank answer.")
        return GradingResult(score=self._typed_score, justification="Fake grader.")
