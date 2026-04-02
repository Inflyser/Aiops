from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class KanbanBoard(Base):
    __tablename__ = "kanban_boards"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    board_order = Column(Integer, default=0, name='board_order')
    
    user_id = Column(String, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User")
    columns = relationship("KanbanColumn", back_populates="board", cascade="all, delete-orphan")


class KanbanColumn(Base):
    __tablename__ = "kanban_columns"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    order = Column(Integer, default=0)
    color = Column(String(7), default="#555555")  # HEX цвет
    is_static = Column(Boolean, default=False)  # Статичная колонка (не может быть удалена)
    is_inbox_category = Column(Boolean, default=False)  # Колонка-категория для Inbox
    
    board_id = Column(String, ForeignKey("kanban_boards.id"), nullable=True)  # NULL для Inbox категорий
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Для Inbox категорий (board_id = NULL)
    
    # Relationships
    board = relationship("KanbanBoard", back_populates="columns")
    user = relationship("User")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan")
