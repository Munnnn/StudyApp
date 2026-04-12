"""
Pure functions — no I/O.

Scoring model:
  typed_score  0-4   (LLM graded, weighted ×2)
  mcq_correct  bool  (binary ×2)
  time_score   0-2   (optional bonus)
  max raw = 12

Mastery thresholds:
  ≥10 → strong
  ≥ 7 → developing
  ≥ 4 → fragile
   <4 → weak
"""
from app.models.attempt import MasteryLevel

RecallGap = str  # "both" | "recognition_only" | "recall_only" | "neither"


def compute_mastery(
    typed_score: int,
    mcq_correct: bool,
    response_time_score: int = 0,
) -> MasteryLevel:
    total = (typed_score * 2) + (2 if mcq_correct else 0) + response_time_score
    if total >= 10:
        return MasteryLevel.strong
    if total >= 7:
        return MasteryLevel.developing
    if total >= 4:
        return MasteryLevel.fragile
    return MasteryLevel.weak


def classify_gap(typed_score: int, mcq_correct: bool) -> RecallGap:
    """Characterise the recall vs. recognition gap for a single attempt."""
    recall_ok = typed_score >= 3
    if recall_ok and mcq_correct:
        return "both"
    if not recall_ok and mcq_correct:
        return "recognition_only"
    if recall_ok and not mcq_correct:
        return "recall_only"
    return "neither"


def response_time_score(response_time_ms: int | None) -> int:
    """Optional speed bonus: ≤15s → 2, ≤30s → 1, else 0."""
    if response_time_ms is None:
        return 0
    seconds = response_time_ms / 1000
    if seconds <= 15:
        return 2
    if seconds <= 30:
        return 1
    return 0
