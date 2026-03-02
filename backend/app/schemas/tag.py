from pydantic import BaseModel, ConfigDict
from typing import Optional

class TagBase(BaseModel):
    name: str
    color: str = "#3B82F6"
    icon: Optional[str] = None

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None

class Tag(TagBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
