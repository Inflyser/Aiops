from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base


class EventTask(Base):
    """Связующая таблица между событиями календаря и задачами"""
    __tablename__ = "event_tasks"
    
    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("calendar_events.id"), nullable=False)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    order = Column(Integer, default=0)  # Порядок задачи в событии
    
    # Relationships
    event = relationship("CalendarEvent", back_populates="event_tasks")
    task = relationship("Task", back_populates="event_tasks")
