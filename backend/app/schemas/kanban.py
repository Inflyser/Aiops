from pydantic import BaseModel, ConfigDict
from typing import Optional


class KanbanColumnBase(BaseModel):
    title: str
    order: int = 0
    color: str = "#555555"


class KanbanColumnCreate(KanbanColumnBase):
    pass


class KanbanColumnUpdate(BaseModel):
    title: Optional[str] = None
    order: Optional[int] = None
    color: Optional[str] = None


class KanbanColumnInDB(KanbanColumnBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str


class KanbanColumn(KanbanColumnInDB):
    pass
