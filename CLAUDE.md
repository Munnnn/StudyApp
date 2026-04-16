# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Pimp App — hospital-style micro-quizzing for USMLE Step 1 and clerkship prep. Two-phase study flow: free-recall (typed answer graded by AI) then MCQ recognition, with adaptive spaced repetition. Users upload flashcard decks via CSV; the AI generates attending-style teaching interactions from each card.

## Architecture

**Monorepo with two independent apps:**

- `backend/` — Python 3.11+ FastAPI + SQLAlchemy 2.0 (async) + Alembic migrations + PostgreSQL 16
- `mobile/` — Expo SDK 54 (React Native 0.81) + Zustand + React Navigation 7

No shared code between them. The mobile app talks to the backend via REST (`X-Device-Id` header for user identity, no auth tokens).

### Backend Structure

```
backend/app/
  main.py              → FastAPI app, CORS, mounts v1 router
  config.py            → pydantic-settings (reads .env)
  db.py                → async SQLAlchemy engine + session factory
  deps.py              → get_current_user (auto-creates user from X-Device-Id header)
  api/v1/              → route modules: users, decks, cards, study, dashboard
  models/              → SQLAlchemy ORM: user, deck, card, generated_question, attempt, schedule_state
  schemas/             → Pydantic request/response models
  services/
    scoring.py         → pure functions: compute_mastery, classify_gap (no I/O)
    scheduling.py      → pure functions: adaptive interval calculation (no I/O)
    generation.py      → orchestrates AI question generation for a card
    grading.py         → orchestrates AI grading of typed answers
    csv_import.py      → CSV/TSV deck import parser
    ai/                → pluggable AI adapters
      base.py          → AIService ABC (generate_teaching, grade_typed_answer)
      factory.py       → get_ai_service() — returns adapter based on AI_PROVIDER env
      anthropic_adapter.py, openai_adapter.py, fake.py
```

### Mobile Structure

```
mobile/src/
  api/client.ts        → fetch wrapper, injects X-Device-Id from Zustand store
  api/endpoints.ts     → typed wrappers for every API route
  state/store.ts       → Zustand global store (deviceId, user, currentAttempt)
  state/device.ts      → device ID persistence (expo-secure-store)
  nav/index.tsx         → navigation tree (Root Stack → Bottom Tabs)
  screens/             → one screen per study phase + deck management + dashboard + settings
  components/          → Button, QuestionCard, MasteryBadge
  theme.ts             → colors/fonts (dark theme)
  notifications/       → local notification scheduling (expo-notifications)
```

### Navigation Flow (mobile)

Root Stack → Onboarding (no user) or Main (has user) → Bottom Tabs: Study | Decks | Dashboard | Settings. Study tab has inner stack: FreeRecall → MCQ → Explanation (screen-replace, no back button).

### Study Flow (critical invariant)

Three-endpoint protocol enforced server-side to prevent answer leakage:

1. `GET /api/v1/study/next` — returns attending_question only. **Never** includes `correct_answer` or `mcq_options`.
2. `POST /api/v1/study/attempts/typed` — locks typed answer, AI grades it, then returns shuffled MCQ options.
3. `POST /api/v1/study/attempts/mcq` — finalizes attempt, computes mastery, updates schedule, returns full explanation.

MCQ option order is deterministic (sha256 of attempt_id as seed). Both client and server reconstruct the same shuffle.

### AI Provider System

Pluggable via `AI_PROVIDER` env var (`anthropic` | `openai` | `fake`). Factory pattern in `services/ai/factory.py`. The `fake` provider returns deterministic results for tests. `generate_teaching()` transforms a flashcard into a full teaching interaction; `grade_typed_answer()` scores free-recall 0-4.

### Scoring & Scheduling (pure functions, no I/O)

- `scoring.py`: mastery = (typed_score * 2) + (mcq_correct ? 2 : 0) + time_bonus. Thresholds: strong >= 10, developing >= 7, fragile >= 4, weak < 4.
- `scheduling.py`: adaptive intervals — strong multiplies by 2.5x (3.5x after 3 consecutive), weak resets to 10min.
- Recognition-only gap (typed wrong + MCQ correct) is tracked as a first-class metric.

## Development Commands

### Prerequisites

Docker (for Postgres), Python 3.11+, Node.js, Expo CLI.

### Start Postgres

```bash
docker-compose up -d
```

### Backend

```bash
cd backend
pip install -e ".[dev]"
cp ../.env.example .env    # then set AI_PROVIDER and API keys
python -m alembic upgrade head
python -m app.seed          # optional: demo deck
uvicorn app.main:app --reload
# API: http://localhost:8000  Swagger: http://localhost:8000/docs
```

### Mobile

```bash
cd mobile
npm install
echo 'EXPO_PUBLIC_API_URL=http://localhost:8000' > .env
npx expo start
```

### Running Tests

```bash
# Unit tests (no DB needed) — scoring, scheduling, CSV import are pure functions
cd backend
pytest tests/test_scoring.py tests/test_scheduling.py tests/test_csv_import.py -v

# Integration tests (needs Postgres running + pimp_test database)
psql -h localhost -U pimp -c "CREATE DATABASE pimp_test;"
TEST_DATABASE_URL=postgresql+asyncpg://pimp:pimp@localhost:5432/pimp_test pytest tests/test_study_flow.py -v

# Run a single test
pytest tests/test_scoring.py::test_name -v
```

### Test Infrastructure

Integration tests use a real Postgres database (not mocks). `conftest.py` overrides `get_db` and `get_ai_service` via FastAPI `dependency_overrides`. There's a `client_wrong_typed` fixture that injects `FakeAIService(typed_score=0)` for recognition-only gap scenarios. Tests use `httpx.AsyncClient` with `ASGITransport`. pytest-asyncio with `asyncio_mode = "auto"`.

## Key Design Decisions

- **No real auth** — device ID is the user identity (MVP scope). `get_current_user` in `deps.py` auto-creates users.
- **Recall integrity** — the three-phase study flow is the core product invariant. `NextQuestionOut` schema deliberately excludes answer fields. Test `test_recall_integrity` verifies this.
- **Pure service functions** — scoring and scheduling have zero I/O, making them trivially testable.
- **AI adapters are lazy-imported** — `factory.py` uses `@lru_cache(maxsize=1)` and deferred imports to avoid loading unused SDKs.

## Environment Variables

Backend reads from `backend/.env` via pydantic-settings. Key vars: `DATABASE_URL`, `AI_PROVIDER` (`fake` for dev/test), `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `PIMP_RUN_LIVE_AI` (set to 1 for live AI integration tests).

Mobile reads `EXPO_PUBLIC_API_URL` from `mobile/.env`.
