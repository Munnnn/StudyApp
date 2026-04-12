"""Pure-function tests for scheduling.py"""
from datetime import datetime, timezone

import pytest
from app.models.attempt import MasteryLevel
from app.services.scheduling import (
    MIN_FRAGILE_MIN,
    MIN_WEAK_MIN,
    MAX_STRONG_MIN,
    MAX_DEVELOPING_MIN,
    compute_next_review,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_weak_resets_to_minimum():
    result = compute_next_review(60, 0, MasteryLevel.weak, now=NOW)
    assert result.interval_min == MIN_WEAK_MIN
    assert result.consecutive_strong == 0


def test_fragile_halves_interval():
    result = compute_next_review(60, 0, MasteryLevel.fragile, now=NOW)
    assert result.interval_min == 30
    assert result.consecutive_strong == 0


def test_fragile_respects_minimum():
    result = compute_next_review(10, 0, MasteryLevel.fragile, now=NOW)
    assert result.interval_min == MIN_FRAGILE_MIN


def test_developing_grows():
    result = compute_next_review(60, 0, MasteryLevel.developing, now=NOW)
    assert result.interval_min == 90
    assert result.consecutive_strong == 0


def test_developing_caps_at_max():
    result = compute_next_review(MAX_DEVELOPING_MIN, 0, MasteryLevel.developing, now=NOW)
    assert result.interval_min == MAX_DEVELOPING_MIN


def test_strong_grows():
    result = compute_next_review(60, 0, MasteryLevel.strong, now=NOW)
    assert result.interval_min == 150  # 60 × 2.5
    assert result.consecutive_strong == 1


def test_strong_high_streak_multiplier():
    result = compute_next_review(60, 3, MasteryLevel.strong, now=NOW)
    assert result.interval_min == 210  # 60 × 3.5
    assert result.consecutive_strong == 4


def test_strong_caps_at_max():
    result = compute_next_review(MAX_STRONG_MIN, 0, MasteryLevel.strong, now=NOW)
    assert result.interval_min == MAX_STRONG_MIN


def test_next_due_at_is_future():
    result = compute_next_review(30, 0, MasteryLevel.developing, now=NOW)
    assert result.next_due_at > NOW
