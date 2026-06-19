from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "active"
    goal_type: str = "concrete"
    target_value: Optional[float] = None
    target_unit: Optional[str] = None
    current_value: float = 0
    deadline: Optional[datetime] = None
    icon: Optional[str] = None
    is_featured: bool = False
    featured_position: Optional[int] = None
    order: int = 0

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    goal_type: Optional[str] = None
    target_value: Optional[float] = None
    target_unit: Optional[str] = None
    current_value: Optional[float] = None
    deadline: Optional[datetime] = None
    icon: Optional[str] = None
    is_featured: Optional[bool] = None
    featured_position: Optional[int] = None
    order: Optional[int] = None

class Goal(GoalBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
