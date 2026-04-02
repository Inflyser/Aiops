from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4

from app.db.base import get_db
from app.schemas.kanban import (
    KanbanBoard, KanbanBoardCreate, KanbanBoardUpdate,
    KanbanColumn, KanbanColumnCreate, KanbanColumnUpdate
)
from app.models.kanban import KanbanBoard as KanbanBoardModel, KanbanColumn as KanbanColumnModel
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

DEFAULT_COLUMNS = [
    {"title": "Inbox", "color": "#4A90E2", "is_static": True},
    {"title": "To Do", "color": "#555555", "is_static": False},
    {"title": "In Progress", "color": "#888888", "is_static": False},
    {"title": "Done", "color": "#cccccc", "is_static": False},
]


# ==================== BOARDS ====================

@router.get("/boards", response_model=List[KanbanBoard])
def read_boards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get boards for user"""
    boards = db.query(KanbanBoardModel).filter(
        KanbanBoardModel.user_id == current_user.id
    ).order_by(KanbanBoardModel.board_order).all()
    
    return boards


@router.post("/boards", response_model=KanbanBoard, status_code=201)
def create_board(
    *,
    db: Session = Depends(get_db),
    board_in: KanbanBoardCreate,
    current_user: User = Depends(get_current_user),
):
    """Create new board"""
    # Get max board_order
    max_order = db.query(KanbanBoardModel.board_order).filter(
        KanbanBoardModel.user_id == current_user.id
    ).order_by(KanbanBoardModel.board_order.desc()).first()
    
    order = (max_order[0] + 1) if max_order and max_order[0] is not None else 0
    
    board = KanbanBoardModel(
        id=str(uuid4()),
        title=board_in.title,
        board_order=order,
        user_id=current_user.id
    )
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


@router.put("/boards/{board_id}", response_model=KanbanBoard)
def update_board(
    *,
    db: Session = Depends(get_db),
    board_id: str,
    board_in: KanbanBoardUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update board"""
    board = db.query(KanbanBoardModel).filter(
        KanbanBoardModel.id == board_id,
        KanbanBoardModel.user_id == current_user.id
    ).first()
    
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    update_data = board_in.model_dump(exclude_unset=True)
    # Rename 'order' to 'board_order' if present
    if 'order' in update_data:
        update_data['board_order'] = update_data.pop('order')
    for field, value in update_data.items():
        setattr(board, field, value)
    
    db.commit()
    db.refresh(board)
    return board


@router.delete("/boards/{board_id}")
def delete_board(
    *,
    db: Session = Depends(get_db),
    board_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete board"""
    board = db.query(KanbanBoardModel).filter(
        KanbanBoardModel.id == board_id,
        KanbanBoardModel.user_id == current_user.id
    ).first()
    
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    db.delete(board)
    db.commit()
    return {"message": "Board deleted successfully"}


@router.post("/boards/reorder")
def reorder_boards(
    board_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reorder boards"""
    for index, board_id in enumerate(board_ids):
        board = db.query(KanbanBoardModel).filter(
            KanbanBoardModel.id == board_id,
            KanbanBoardModel.user_id == current_user.id
        ).first()
        if (board):
            board.board_order = index
    
    db.commit()
    return {"message": "Boards reordered successfully"}


# ==================== COLUMNS ====================

@router.get("/boards/{board_id}/columns", response_model=List[KanbanColumn])
def read_columns(
    board_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get columns for board"""
    # Check that board exists and belongs to user
    board = db.query(KanbanBoardModel).filter(
        KanbanBoardModel.id == board_id,
        KanbanBoardModel.user_id == current_user.id
    ).first()
    
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    columns = db.query(KanbanColumnModel).filter(
        KanbanColumnModel.board_id == board_id
    ).order_by(KanbanColumnModel.order).all()
    
    # Return columns without creating default ones
    # Boards are created empty now, users create their own columns
    return columns


@router.get("/inbox/categories", response_model=List[KanbanColumn])
def read_inbox_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get Inbox category columns"""
    # Get all user's boards first
    user_board_ids = db.query(KanbanBoardModel.id).filter(
        KanbanBoardModel.user_id == current_user.id
    ).all()
    user_board_ids = [board.id for board in user_board_ids]
    
    # Get inbox categories (board_id is NULL) OR categories from user's boards
    columns = db.query(KanbanColumnModel).filter(
        (KanbanColumnModel.board_id == None) |
        (KanbanColumnModel.board_id.in_(user_board_ids))
    ).filter(
        KanbanColumnModel.is_inbox_category == True
    ).order_by(KanbanColumnModel.order).all()
    
    return columns


@router.post("/boards/{board_id}/columns", response_model=KanbanColumn, status_code=201)
def create_column(
    *,
    board_id: str,
    db: Session = Depends(get_db),
    column_in: KanbanColumnCreate,
    current_user: User = Depends(get_current_user),
):
    """Create new column"""
    # Check that board exists and belongs to user
    board = db.query(KanbanBoardModel).filter(
        KanbanBoardModel.id == board_id,
        KanbanBoardModel.user_id == current_user.id
    ).first()
    
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # Get max order
    max_order = db.query(KanbanColumnModel.order).filter(
        KanbanColumnModel.board_id == board_id
    ).order_by(KanbanColumnModel.order.desc()).first()
    
    order = (max_order[0] + 1) if max_order and max_order[0] is not None else 0
    
    column = KanbanColumnModel(
        id=str(uuid4()),
        title=column_in.title,
        color=column_in.color,
        order=order,
        is_static=column_in.is_static,
        is_inbox_category=column_in.is_inbox_category,
        board_id=board_id
    )
    db.add(column)
    db.commit()
    db.refresh(column)
    return column


@router.post("/inbox/categories", response_model=KanbanColumn, status_code=201)
def create_inbox_category(
    *,
    db: Session = Depends(get_db),
    column_in: KanbanColumnCreate,
    current_user: User = Depends(get_current_user),
):
    """Create new Inbox category column"""
    # Get max order for Inbox categories (board_id is NULL)
    max_order = db.query(KanbanColumnModel.order).filter(
        KanbanColumnModel.board_id == None,
        KanbanColumnModel.user_id == current_user.id
    ).order_by(KanbanColumnModel.order.desc()).first()
    
    order = (max_order[0] + 1) if max_order and max_order[0] is not None else 0
    
    column = KanbanColumnModel(
        id=str(uuid4()),
        title=column_in.title,
        color=column_in.color,
        order=order,
        is_static=column_in.is_static,
        is_inbox_category=True,
        board_id=None,  # NULL для Inbox категорий
        user_id=current_user.id  # Устанавливаем user_id для Inbox категорий
    )
    db.add(column)
    db.commit()
    db.refresh(column)
    return column


@router.put("/columns/{column_id}", response_model=KanbanColumn)
def update_column(
    *,
    db: Session = Depends(get_db),
    column_id: str,
    column_in: KanbanColumnUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update column"""
    column = db.query(KanbanColumnModel).join(KanbanBoardModel).filter(
        KanbanColumnModel.id == column_id,
        KanbanBoardModel.user_id == current_user.id
    ).first()
    
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    update_data = column_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(column, field, value)
    
    db.commit()
    db.refresh(column)
    return column


@router.delete("/columns/{column_id}")
def delete_column(
    *,
    db: Session = Depends(get_db),
    column_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete column"""
    column = db.query(KanbanColumnModel).join(KanbanBoardModel).filter(
        KanbanColumnModel.id == column_id,
        KanbanBoardModel.user_id == current_user.id
    ).first()
    
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    if column.is_static:
        raise HTTPException(status_code=400, detail="Cannot delete static column")
    
    db.delete(column)
    db.commit()
    return {"message": "Column deleted successfully"}


@router.post("/columns/reorder")
def reorder_columns(
    column_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reorder columns"""
    for index, column_id in enumerate(column_ids):
        column = db.query(KanbanColumnModel).join(KanbanBoardModel).filter(
            KanbanColumnModel.id == column_id,
            KanbanBoardModel.user_id == current_user.id
        ).first()
        if (column):
            column.order = index
    
    db.commit()
    return {"message": "Columns reordered successfully"}
