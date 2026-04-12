# Pimp App

Hospital-style micro-quizzing for USMLE Step 1 and clerkship prep.

Turns user-uploaded flashcards into two-phase (free-recall → MCQ) attending-style teaching interactions. Scores recall and recognition independently. Adapts spacing to your weak spots.

---

## Architecture

```
mobile/    Expo (React Native) — iOS + Android
backend/   FastAPI + SQLAlchemy + Alembic — Python 3.11+
docker-compose.yml — PostgreSQL 16 (local dev)
```

---

## Quick start (local dev)

### 1. Start Postgres

```bash
docker-compose up -d
```

### 2. Backend

```bash
cd backend

# Install (use uv or pip)
pip install -e ".[dev]"

# Copy and edit env
cp ../.env.example .env
# Edit .env — set AI_PROVIDER=anthropic (or openai or fake) and add your API key

# Run migrations
python -m alembic upgrade head

# Seed demo deck (optional)
python -m app.seed

# Start server
uvicorn app.main:app --reload
# → API at http://localhost:8000
# → Swagger docs at http://localhost:8000/docs
```

### 3. Mobile app

```bash
cd mobile
npm install

# Set your backend URL (replace with your LAN IP if testing on device)
echo 'EXPO_PUBLIC_API_URL=http://localhost:8000' > .env

# Start Expo
npx expo start
# Scan QR with Expo Go on your phone, or press 'i' for iOS sim / 'a' for Android
```

---

## Environment variables (backend `.env`)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://pimp:pimp@localhost:5432/pimp` | Postgres connection |
| `AI_PROVIDER` | `fake` | `anthropic` \| `openai` \| `fake` |
| `ANTHROPIC_API_KEY` | — | Required if `AI_PROVIDER=anthropic` |
| `OPENAI_API_KEY` | — | Required if `AI_PROVIDER=openai` |
| `PIMP_RUN_LIVE_AI` | `0` | Set to `1` to run live-AI integration tests |

### Mobile env (`.env` in `mobile/`)

| Variable | Default | Description |
|---|---|---|
| `EXPO_PUBLIC_API_URL` | `http://localhost:8000` | Backend URL (use LAN IP for device) |

---

## Running tests

```bash
cd backend

# Unit tests (no DB needed)
pytest tests/test_scoring.py tests/test_scheduling.py tests/test_csv_import.py -v

# Integration tests (need Postgres running)
# Create test DB first:
#   psql -h localhost -U pimp -c "CREATE DATABASE pimp_test;"
TEST_DATABASE_URL=postgresql+asyncpg://pimp:pimp@localhost:5432/pimp_test pytest tests/test_study_flow.py -v
```

---

## Study flow (recall integrity)

The two-phase flow is enforced at the **API layer**, not just the UI:

```
GET  /api/v1/study/next           → attending_question ONLY (no answer, no MCQ options)
POST /api/v1/study/attempts/typed → locks typed answer, returns shuffled MCQ options
POST /api/v1/study/attempts/mcq   → finalises attempt, returns full explanation
```

`/study/next` never includes `correct_answer` or `mcq_options` — verified by `test_recall_integrity` in the test suite.

---

## CSV import format

```csv
front,back,system_tag,topic_tag,difficulty
What causes hypercalcemia with low PTH?,Malignancy (PTHrP),renal,calcium,3
```

- Tab-separated files also accepted (auto-detected)
- `system` and `topic` are aliases for `system_tag` / `topic_tag`
- `difficulty` is 1–5 (default 2)
- Extra columns are ignored

---

## AI providers

Switch providers via `AI_PROVIDER` env var. The pluggable adapter interface means you can add more providers later without changing application code.

| Provider | Generation model | Grading model |
|---|---|---|
| `anthropic` | claude-haiku-4-5-20251001 | claude-sonnet-4-6 |
| `openai` | gpt-4o-mini | gpt-4o |
| `fake` | deterministic (for tests) | deterministic |

---

## Scoring model

```
Mastery = (typed_score × 2) + (mcq_correct ? 2 : 0) + time_bonus
  strong     ≥ 10
  developing ≥ 7
  fragile    ≥ 4
  weak        < 4
```

**Recognition-only gap** (`typed wrong + MCQ correct`) is tracked separately in the dashboard — the key product differentiator.

---

## Notifications

Local only (via `expo-notifications`). Configure interval (10m / 30m / 1h / 2h) and quiet hours in the Settings tab. Notification tap deep-links directly to the Study tab.

---

## Out of scope for MVP

- Real auth / multi-device sync
- Voice mode
- App Store submission
- Offline mode
- Anki `.apkg` binary import
