from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, ARRAY, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    completed = Column(Boolean, default=False)
    due_date = Column(DateTime(timezone=True))
    priority = Column(String(20), default="medium")  # low, medium, high
    tags = Column(ARRAY(String))
    order = Column(Integer, default=0)
    
    user_id = Column(String, ForeignKey("users.id"))
    project_id = Column(String, nullable=True)  # Временно без ForeignKey, так как Project может не существовать
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    subtasks = relationship("Subtask", back_populates="task", cascade="all, delete-orphan")

class Subtask(Base):
    __tablename__ = "subtasks"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    completed = Column(Boolean, default=False)
    task_id = Column(String, ForeignKey("tasks.id"))
    order = Column(Integer, default=0)
    
    task = relationship("Task", back_populates="subtasks")