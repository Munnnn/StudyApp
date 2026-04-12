from fastapi import APIRouter

from app.api.v1 import users, decks, cards, study, dashboard

router = APIRouter(prefix="/api/v1")
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(decks.router, prefix="/decks", tags=["decks"])
router.include_router(cards.router, prefix="/cards", tags=["cards"])
router.include_router(study.router, prefix="/study", tags=["study"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
