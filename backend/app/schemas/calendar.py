from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start: datetime
    end: datetime
    all_day: bool = False
    color: str = "#4a5568"
    priority: str = "medium"
    tag_id: Optional[str] = None
    recurrence_type: Optional[str] = None  # 'weekly', 'monthly', 'yearly'
    recurrence_days: Optional[str] = None  # дни недели через запятую: "0,2,4"
    recurrence_end_date: Optional[datetime] = None
    recurrence_count: Optional[int] = None

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    all_day: Optional[bool] = None
    color: Optional[str] = None
    priority: Optional[str] = None
    tag_id: Optional[str] = None
    recurrence_type: Optional[str] = None
    recurrence_days: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None
    recurrence_count: Optional[int] = None

class CalendarEvent(CalendarEventBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    original_id: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

