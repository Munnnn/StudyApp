from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User


async def get_current_user(
    x_device_id: str = Header(..., alias="X-Device-Id"),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not x_device_id or len(x_device_id) < 8:
        raise HTTPException(status_code=400, detail="Invalid X-Device-Id header")

    result = await db.execute(select(User).where(User.device_id == x_device_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(device_id=x_device_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
