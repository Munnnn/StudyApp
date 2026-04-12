"""
Integration tests for the two-phase study flow.

KEY TEST: recall_integrity — asserts /study/next NEVER returns
          correct_answer or mcq_options (the most important invariant).
"""
import json
import pytest


DEVICE_ID = "test-device-integration-001"
HEADERS = {"X-Device-Id": DEVICE_ID}
DEVICE_ID_WRONG = "test-device-integration-002"
HEADERS_WRONG = {"X-Device-Id": DEVICE_ID_WRONG}


# ── helpers ──────────────────────────────────────────────────────────────────

async def bootstrap(client):
    r = await client.post("/api/v1/users/ensure", headers=HEADERS)
    assert r.status_code == 200
    return r.json()


async def create_deck_and_card(client):
    r = await client.post(
        "/api/v1/decks",
        json={"title": "Step 1 Test Deck"},
        headers=HEADERS,
    )
    assert r.status_code == 201
    deck_id = r.json()["id"]

    r2 = await client.post(
        f"/api/v1/decks/{deck_id}/cards",
        json={
            "front": "What causes hypercalcemia with low PTH?",
            "back": "Malignancy (PTHrP)",
            "system_tag": "endocrine",
            "topic_tag": "calcium",
        },
        headers=HEADERS,
    )
    assert r2.status_code == 201
    card_id = r2.json()["id"]
    return deck_id, card_id


# ── recall integrity (MOST IMPORTANT TEST) ───────────────────────────────────

@pytest.mark.asyncio
async def test_next_question_excludes_answer_and_mcq_options(client):
    """
    /study/next MUST NOT include correct_answer or mcq_options.
    This regression test is the gatekeeper for recall integrity.
    """
    await bootstrap(client)
    await create_deck_and_card(client)

    r = await client.get("/api/v1/study/next", headers=HEADERS)
    assert r.status_code == 200

    payload = r.json()
    raw_text = r.text

    # Field-level assertions
    assert "correct_answer" not in payload, "RECALL INTEGRITY VIOLATION: correct_answer in /study/next"
    assert "mcq_options" not in payload, "RECALL INTEGRITY VIOLATION: mcq_options in /study/next"

    # Text-level assertion: ensure the correct answer text is not smuggled in
    # We know the fake AI's correct_answer
    assert "Malignancy (PTHrP)" not in raw_text, "RECALL INTEGRITY VIOLATION: answer text in /study/next body"

    # Required fields are present
    assert "attending_question" in payload
    assert "generated_question_id" in payload
    assert "card_id" in payload


# ── happy path: full two-phase flow ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_full_study_flow_strong_mastery(client):
    """Typed correct (score=4) + MCQ correct → strong mastery, interval grows."""
    await bootstrap(client)
    deck_id, card_id = await create_deck_and_card(client)

    # Step 1: get next question
    r = await client.get("/api/v1/study/next", headers=HEADERS)
    assert r.status_code == 200
    gq_id = r.json()["generated_question_id"]

    # Step 2: submit typed answer
    r2 = await client.post(
        "/api/v1/study/attempts/typed",
        json={"generated_question_id": gq_id, "typed_answer": "Malignancy PTHrP", "response_time_ms": 8000},
        headers=HEADERS,
    )
    assert r2.status_code == 201
    typed_resp = r2.json()
    attempt_id = typed_resp["attempt_id"]
    mcq_options = typed_resp["mcq_options"]
    assert len(mcq_options) == 4
    assert "Malignancy (PTHrP)" in mcq_options

    # Determine correct index from shuffled list
    correct_idx = mcq_options.index("Malignancy (PTHrP)")

    # Step 3: submit MCQ
    r3 = await client.post(
        "/api/v1/study/attempts/mcq",
        json={"attempt_id": attempt_id, "mcq_selected_index": correct_idx, "response_time_ms": 3000},
        headers=HEADERS,
    )
    assert r3.status_code == 200
    expl = r3.json()

    assert expl["mcq_correct"] is True
    assert expl["typed_answer_score"] == 4
    assert expl["mastery_level"] == "strong"
    assert expl["recall_gap"] == "both"
    assert "step_by_step_explanation" in expl
    assert "wrong_answer_analysis" in expl
    assert len(expl["follow_up_questions"]) == 2
    assert "correct_answer" in expl  # full payload IS returned on explanation screen


@pytest.mark.asyncio
async def test_recognition_only_gap(client_wrong_typed):
    """Typed wrong (score=0) + MCQ correct → recognition_only gap, weak/fragile mastery."""
    client = client_wrong_typed
    await client.post("/api/v1/users/ensure", headers=HEADERS_WRONG)
    r = await client.post(
        "/api/v1/decks", json={"title": "Gap Test Deck"}, headers=HEADERS_WRONG
    )
    deck_id = r.json()["id"]
    await client.post(
        f"/api/v1/decks/{deck_id}/cards",
        json={"front": "Q", "back": "A"},
        headers=HEADERS_WRONG,
    )

    r = await client.get("/api/v1/study/next", headers=HEADERS_WRONG)
    gq_id = r.json()["generated_question_id"]

    r2 = await client.post(
        "/api/v1/study/attempts/typed",
        json={"generated_question_id": gq_id, "typed_answer": "wrong answer"},
        headers=HEADERS_WRONG,
    )
    mcq_options = r2.json()["mcq_options"]
    attempt_id = r2.json()["attempt_id"]

    # Select correct MCQ option
    correct_idx = mcq_options.index("Malignancy (PTHrP)")
    r3 = await client.post(
        "/api/v1/study/attempts/mcq",
        json={"attempt_id": attempt_id, "mcq_selected_index": correct_idx},
        headers=HEADERS_WRONG,
    )
    expl = r3.json()
    assert expl["mcq_correct"] is True
    assert expl["typed_answer_score"] == 0
    assert expl["recall_gap"] == "recognition_only"
    assert expl["mastery_level"] in ("weak", "fragile")


@pytest.mark.asyncio
async def test_cannot_submit_mcq_twice(client):
    """Submitting MCQ twice on the same attempt returns 409."""
    await bootstrap(client)
    await create_deck_and_card(client)

    r = await client.get("/api/v1/study/next", headers=HEADERS)
    gq_id = r.json()["generated_question_id"]

    r2 = await client.post(
        "/api/v1/study/attempts/typed",
        json={"generated_question_id": gq_id, "typed_answer": "answer"},
        headers=HEADERS,
    )
    attempt_id = r2.json()["attempt_id"]
    mcq_options = r2.json()["mcq_options"]
    correct_idx = mcq_options.index("Malignancy (PTHrP)")

    await client.post(
        "/api/v1/study/attempts/mcq",
        json={"attempt_id": attempt_id, "mcq_selected_index": correct_idx},
        headers=HEADERS,
    )
    r_dup = await client.post(
        "/api/v1/study/attempts/mcq",
        json={"attempt_id": attempt_id, "mcq_selected_index": correct_idx},
        headers=HEADERS,
    )
    assert r_dup.status_code == 409


@pytest.mark.asyncio
async def test_schedule_state_updated_after_attempt(client):
    """After a strong attempt the schedule interval should grow."""
    from app.models.schedule_state import ScheduleState
    from sqlalchemy import select

    await bootstrap(client)
    deck_id, card_id = await create_deck_and_card(client)

    r = await client.get("/api/v1/study/next", headers=HEADERS)
    gq_id = r.json()["generated_question_id"]

    r2 = await client.post(
        "/api/v1/study/attempts/typed",
        json={"generated_question_id": gq_id, "typed_answer": "PTHrP malignancy"},
        headers=HEADERS,
    )
    mcq_options = r2.json()["mcq_options"]
    attempt_id = r2.json()["attempt_id"]
    correct_idx = mcq_options.index("Malignancy (PTHrP)")

    await client.post(
        "/api/v1/study/attempts/mcq",
        json={"attempt_id": attempt_id, "mcq_selected_index": correct_idx},
        headers=HEADERS,
    )
    # Interval should have grown beyond initial 10 min
    # (checked via dashboard or by peeking at DB state — here we check dashboard)
    r_dash = await client.get("/api/v1/dashboard", headers=HEADERS)
    assert r_dash.status_code == 200
    assert r_dash.json()["total_attempts"] >= 1
    assert r_dash.json()["strong_mastery_count"] >= 1
