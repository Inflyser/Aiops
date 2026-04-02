from pydantic import BaseModel, ConfigDict
from typing import Optional


# Kanban Board Schemas
class KanbanBoardBase(BaseModel):
    title: str
    board_order: int = 0


class KanbanBoardCreate(KanbanBoardBase):
    pass


class KanbanBoardUpdate(BaseModel):
    title: Optional[str] = None
    order: Optional[int] = None


class KanbanBoardInDB(KanbanBoardBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str


class KanbanBoard(KanbanBoardInDB):
    pass


# Kanban Column Schemas
class KanbanColumnBase(BaseModel):
    title: str
    order: int = 0
    color: str = "#555555"
    is_static: bool = False
    is_inbox_category: bool = False


class KanbanColumnCreate(KanbanColumnBase):
    board_id: Optional[str] = None  # NULL для Inbox категорий


class KanbanColumnUpdate(BaseModel):
    title: Optional[str] = None
    order: Optional[int] = None
    color: Optional[str] = None
    is_static: Optional[bool] = None
    is_inbox_category: Optional[bool] = None


class KanbanColumnInDB(KanbanColumnBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    board_id: Optional[str] = None  # NULL для Inbox категорий


class KanbanColumn(KanbanColumnInDB):
    pass
