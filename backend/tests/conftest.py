"""
Test fixtures.
Uses a real PostgreSQL test database (DATABASE_URL from env or defaults to
postgresql+asyncpg://pimp:pimp@localhost:5432/pimp_test).
All tests run inside a rolled-back transaction.
The FakeAIService is injected via FastAPI dependency_overrides.
"""
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import Base, get_db
from app.main import app
from app.services.ai.factory import get_ai_service
from tests.fake_ai import FakeAIService

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://pimp:pimp@localhost:5432/pimp_test",
)

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(create_tables):
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def override_db():
        yield db_session

    fake_ai = FakeAIService(typed_score=4)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_ai_service] = lambda: fake_ai

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_wrong_typed(db_session):
    """Client where AI always returns typed_score=0 (recognition-only scenario)."""
    async def override_db():
        yield db_session

    fake_ai = FakeAIService(typed_score=0)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_ai_service] = lambda: fake_ai

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
