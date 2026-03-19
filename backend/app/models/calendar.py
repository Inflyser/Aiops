from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start = Column(DateTime(timezone=True), nullable=False)
    end = Column(DateTime(timezone=True), nullable=False)
    all_day = Column(Boolean, default=False)
    color = Column(String(7), default="#3B82F6")  # HEX цвет
    priority = Column(String(20), default="medium")  # low, medium, high
    tag_id = Column(String, ForeignKey("tags.id"), nullable=True)  # Связь с тегом
    
    # Поля для повторения
    recurrence_type = Column(String(20), nullable=True)  # 'weekly', 'monthly', 'yearly'
    recurrence_days = Column(String(20), nullable=True)  # дни недели через запятую: "0,2,4" (Пн,Ср,Пт)
    recurrence_end_date = Column(DateTime(timezone=True), nullable=True)  # дата окончания повторения
    recurrence_count = Column(Integer, nullable=True)  # количество повторений
    
    user_id = Column(String, ForeignKey("users.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="calendar_events")
    tag = relationship("Tag", foreign_keys=[tag_id])
    event_tasks = relationship("EventTask", back_populates="event", cascade="all, delete-orphan")
