from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=False, default="#3B82F6")  # HEX цвет
    icon = Column(String(100), nullable=True)  # имя файла иконки
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    user = relationship("User", back_populates="tags")
