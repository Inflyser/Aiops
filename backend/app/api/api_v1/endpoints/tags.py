from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4

from app.db.base import get_db
from app.models.tag import Tag
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.tag import TagCreate, TagUpdate, Tag as TagSchema

router = APIRouter()

@router.get("/", response_model=List[TagSchema])
def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить все теги пользователя"""
    tags = db.query(Tag).filter(Tag.user_id == current_user.id).all()
    return tags

@router.post("/", response_model=TagSchema, status_code=201)
def create_tag(
    *,
    db: Session = Depends(get_db),
    tag_in: TagCreate,
    current_user: User = Depends(get_current_user),
):
    """Создать новый тег"""
    tag = Tag(
        id=str(uuid4()),
        name=tag_in.name,
        color=tag_in.color,
        user_id=current_user.id
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@router.put("/{tag_id}", response_model=TagSchema)
def update_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: str,
    tag_in: TagUpdate,
    current_user: User = Depends(get_current_user),
):
    """Обновить тег"""
    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.user_id == current_user.id
    ).first()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    update_data = tag_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(tag, field, value)
    
    db.commit()
    db.refresh(tag)
    return tag

@router.delete("/{tag_id}")
def delete_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: str,
    current_user: User = Depends(get_current_user),
):
    """Удалить тег"""
    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.user_id == current_user.id
    ).first()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Сначала очищаем tag_id у всех связанных событий
    from app.models.calendar import CalendarEvent
    db.query(CalendarEvent).filter(
        CalendarEvent.tag_id == tag_id
    ).update({"tag_id": None})
    
    db.delete(tag)
    db.commit()
    return {"message": "Tag deleted", "id": tag_id}
