from pydantic import BaseModel, ConfigDict


class EventTaskBase(BaseModel):
    event_id: str
    task_id: str
    order: int = 0


class EventTaskCreate(EventTaskBase):
    pass


class EventTaskUpdate(BaseModel):
    order: int = None


class EventTask(EventTaskBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
