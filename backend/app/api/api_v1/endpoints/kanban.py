from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4

from app.db.base import get_db
from app.schemas.kanban import KanbanColumn, KanbanColumnCreate, KanbanColumnUpdate
from app.models.kanban import KanbanColumn as KanbanColumnModel
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

DEFAULT_COLUMNS = [
    {"title": "To Do", "color": "#555555"},
    {"title": "In Progress", "color": "#888888"},
    {"title": "Done", "color": "#cccccc"},
]


@router.get("/", response_model=List[KanbanColumn])
def read_columns(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить колонки пользователя"""
    columns = db.query(KanbanColumnModel).filter(
        KanbanColumnModel.user_id == current_user.id
    ).order_by(KanbanColumnModel.order).all()
    
    # Если колонок нет - создаем дефолтные
    if not columns:
        for i, col_data in enumerate(DEFAULT_COLUMNS):
            column = KanbanColumnModel(
                id=str(uuid4()),
                title=col_data["title"],
                color=col_data["color"],
                order=i,
                user_id=current_user.id
            )
            db.add(column)
        db.commit()
        columns = db.query(KanbanColumnModel).filter(
            KanbanColumnModel.user_id == current_user.id
        ).order_by(KanbanColumnModel.order).all()
    
    return columns


@router.post("/", response_model=KanbanColumn, status_code=201)
def create_column(
    *,
    db: Session = Depends(get_db),
    column_in: KanbanColumnCreate,
    current_user: User = Depends(get_current_user),
):
    """Создать новую колонку"""
    # Получаем максимальный order
    max_order = db.query(KanbanColumnModel.order).filter(
        KanbanColumnModel.user_id == current_user.id
    ).order_by(KanbanColumnModel.order.desc()).first()
    
    order = (max_order[0] + 1) if max_order and max_order[0] is not None else 0
    
    column = KanbanColumnModel(
        id=str(uuid4()),
        title=column_in.title,
        color=column_in.color,
        order=order,
        user_id=current_user.id
    )
    db.add(column)
    db.commit()
    db.refresh(column)
    return column


@router.put("/{column_id}", response_model=KanbanColumn)
def update_column(
    *,
    db: Session = Depends(get_db),
    column_id: str,
    column_in: KanbanColumnUpdate,
    current_user: User = Depends(get_current_user),
):
    """Обновить колонку"""
    column = db.query(KanbanColumnModel).filter(
        KanbanColumnModel.id == column_id,
        KanbanColumnModel.user_id == current_user.id
    ).first()
    
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    update_data = column_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(column, field, value)
    
    db.commit()
    db.refresh(column)
    return column


@router.delete("/{column_id}")
def delete_column(
    *,
    db: Session = Depends(get_db),
    column_id: str,
    current_user: User = Depends(get_current_user),
):
    """Удалить колонку"""
    column = db.query(KanbanColumnModel).filter(
        KanbanColumnModel.id == column_id,
        KanbanColumnModel.user_id == current_user.id
    ).first()
    
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    # Удаляем все задачи в этой колонке (или переносим в первую колонку)
    db.delete(column)
    db.commit()
    return {"message": "Column deleted successfully"}


@router.post("/reorder")
def reorder_columns(
    *,
    db: Session = Depends(get_db),
    column_ids: List[str],
    current_user: User = Depends(get_current_user),
):
    """Изменить порядок колонок"""
    for i, column_id in enumerate(column_ids):
        column = db.query(KanbanColumnModel).filter(
            KanbanColumnModel.id == column_id,
            KanbanColumnModel.user_id == current_user.id
        ).first()
        if column:
            column.order = i
    
    db.commit()
    return {"message": "Columns reordered successfully"}
