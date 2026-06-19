from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Goal(Base):
    __tablename__ = "goals"

    id = Column(String, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")
    goal_type = Column(String(50), default="concrete")
    target_value = Column(Float, nullable=True)
    target_unit = Column(String(50), nullable=True)
    current_value = Column(Float, default=0)
    deadline = Column(DateTime(timezone=True), nullable=True)
    icon = Column(String(100), nullable=True)
    is_featured = Column(Boolean, default=False)
    featured_position = Column(Integer, nullable=True)
    order = Column(Integer, default=0)

    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="goals")
