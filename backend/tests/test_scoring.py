"""Pure-function tests for scoring.py"""
import pytest
from app.models.attempt import MasteryLevel
from app.services.scoring import classify_gap, compute_mastery, response_time_score


# ── compute_mastery ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("typed,mcq,time_s,expected", [
    # Strong: 4×2 + 2 + 2 = 10
    (4, True,  0,  MasteryLevel.strong),
    (4, True,  10_000, MasteryLevel.strong),  # fast answer bonus
    # Developing: 3×2 + 2 = 8
    (3, True,  0,  MasteryLevel.developing),
    # Fragile: 2×2 + 2 = 6... wait 6 >= 4 → fragile
    (2, True,  0,  MasteryLevel.fragile),
    # Weak: 0×2 + 0 = 0
    (0, False, 0,  MasteryLevel.weak),
    # Recognition only: 0×2 + 2 = 2 → weak
    (0, True,  0,  MasteryLevel.weak),
    # Developing borderline: 2×2 + 0 + 0 = 4 → fragile
    (2, False, 0,  MasteryLevel.fragile),
])
def test_compute_mastery(typed, mcq, time_s, expected):
    t_score = response_time_score(time_s) if time_s else 0
    assert compute_mastery(typed, mcq, t_score) == expected


# ── classify_gap ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("typed,mcq,expected", [
    (4, True,  "both"),
    (3, True,  "both"),
    (0, True,  "recognition_only"),
    (1, True,  "recognition_only"),
    (4, False, "recall_only"),
    (0, False, "neither"),
])
def test_classify_gap(typed, mcq, expected):
    assert classify_gap(typed, mcq) == expected


# ── response_time_score ──────────────────────────────────────────────────────

def test_fast_response():
    assert response_time_score(10_000) == 2  # 10 seconds

def test_medium_response():
    assert response_time_score(20_000) == 1  # 20 seconds

def test_slow_response():
    assert response_time_score(60_000) == 0  # 60 seconds

def test_none_response():
    assert response_time_score(None) == 0
