"""
Pure functions — no I/O.

Adaptive interval logic:
  STRONG     → interval ×2.5 (×3.5 if consecutive_strong ≥3), cap 72h
  DEVELOPING → interval ×1.5, cap 12h
  FRAGILE    → interval ÷2, min 15m
  WEAK       → interval = 10m (rapid resurface)
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.models.attempt import MasteryLevel

MAX_STRONG_MIN = 72 * 60     # 72 hours
MAX_DEVELOPING_MIN = 12 * 60  # 12 hours
MIN_FRAGILE_MIN = 15
MIN_WEAK_MIN = 10


@dataclass
class ScheduleUpdate:
    next_due_at: datetime
    interval_min: int
    consecutive_strong: int


def compute_next_review(
    current_interval_min: int,
    current_consecutive_strong: int,
    mastery: MasteryLevel,
    now: datetime | None = None,
) -> ScheduleUpdate:
    if now is None:
        now = datetime.now(timezone.utc)

    if mastery == MasteryLevel.strong:
        multiplier = 3.5 if current_consecutive_strong >= 3 else 2.5
        new_interval = min(int(current_interval_min * multiplier), MAX_STRONG_MIN)
        new_consecutive = current_consecutive_strong + 1
    elif mastery == MasteryLevel.developing:
        new_interval = min(int(current_interval_min * 1.5), MAX_DEVELOPING_MIN)
        new_consecutive = 0
    elif mastery == MasteryLevel.fragile:
        new_interval = max(current_interval_min // 2, MIN_FRAGILE_MIN)
        new_consecutive = 0
    else:  # weak
        new_interval = MIN_WEAK_MIN
        new_consecutive = 0

    return ScheduleUpdate(
        next_due_at=now + timedelta(minutes=new_interval),
        interval_min=new_interval,
        consecutive_strong=new_consecutive,
    )
