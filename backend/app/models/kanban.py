from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class KanbanColumn(Base):
    __tablename__ = "kanban_columns"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    order = Column(Integer, default=0)
    color = Column(String(7), default="#555555")  # HEX цвет
    is_static = Column(Boolean, default=False)  # Статичная колонка (не может быть удалена)
    
    user_id = Column(String, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="kanban_columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan")
