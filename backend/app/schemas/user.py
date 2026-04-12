import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserOut(BaseModel):
    id: uuid.UUID
    device_id: str
    display_name: Optional[str]
    notification_interval_min: int
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    paused: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    notification_interval_min: Optional[int] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    paused: Optional[bool] = None
