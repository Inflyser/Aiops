from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Для Render.com PostgreSQL используем pool_pre_ping для автоматического переподключения
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Автоматически переподключается при разрыве соединения
    pool_recycle=300,    # Переиспользование соединений каждые 5 минут
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()