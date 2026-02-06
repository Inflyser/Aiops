from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[datetime] = None
    priority: str = "medium"
    tags: List[str] = []
    project_id: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    project_id: Optional[str] = None
    order: Optional[int] = None

class TaskInDB(TaskBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class Task(TaskInDB):
    pass

class SubtaskBase(BaseModel):
    title: str
    completed: bool = False

class SubtaskCreate(SubtaskBase):
    task_id: str

class Subtask(SubtaskBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    task_id: str
    order: int