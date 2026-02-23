from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError
from app.db.base import get_db
from app.models.user import User
from uuid import uuid4

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Получить текущего пользователя.
    Временная реализация для тестирования - возвращает первого пользователя или создает тестового.
    В продакшене нужно добавить проверку JWT токена.
    """
    # Временная реализация для разработки
    # В продакшене нужно проверять JWT токен из заголовка Authorization
    
    try:
        # Пытаемся найти первого активного пользователя
        user = db.query(User).filter(User.is_active == True).first()
        
        if not user:
            # Создаем тестового пользователя если его нет
            user = User(
                id=str(uuid4()),
                email="test@example.com",
                hashed_password="test",  # В продакшене нужно хешировать пароль
                full_name="Test User",
                is_active=True,
                is_superuser=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
    except ProgrammingError as e:
        # Если таблица не существует, возвращаем понятную ошибку
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialized. Please run migrations."
        )




