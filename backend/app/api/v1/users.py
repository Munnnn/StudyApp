from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate

router = APIRouter()


@router.post("/ensure", response_model=UserOut)
async def ensure_user(user: User = Depends(get_current_user)):
    """Bootstrap: called on first app launch. Creates or returns the device user."""
    return user


@router.patch("/me", response_model=UserOut)
async def update_user(
    body: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user
