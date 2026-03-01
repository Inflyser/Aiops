from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel

from app.db.base import get_db
from app.schemas.task import Task, TaskCreate, TaskUpdate, TaskInDB
from app.models.task import Task as TaskModel
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Task])
def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None,
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Получить задачи пользователя"""
    query = db.query(TaskModel).filter(TaskModel.user_id == current_user.id)
    
    if completed is not None:
        query = query.filter(TaskModel.completed == completed)
    
    if project_id:
        query = query.filter(TaskModel.project_id == project_id)
    
    tasks = query.order_by(TaskModel.order, TaskModel.created_at.desc()).offset(skip).limit(limit).all()
    return tasks

@router.post("/", response_model=Task, status_code=201)
def create_task(
    *,
    db: Session = Depends(get_db),
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
):
    """Создать новую задачу"""
    task_data = task_in.model_dump()
    task_data["id"] = str(uuid4())
    task_data["user_id"] = current_user.id
    
    # Получаем максимальный order для сортировки
    project_filter = TaskModel.project_id == task_in.project_id
    if task_in.project_id is None:
        project_filter = TaskModel.project_id.is_(None)
        
    max_order = db.query(TaskModel.order).filter(
        TaskModel.user_id == current_user.id,
        project_filter
    ).order_by(TaskModel.order.desc()).first()
    
    task_data["order"] = (max_order[0] + 1) if max_order and max_order[0] is not None else 0
    
    task = TaskModel(**task_data)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.put("/{task_id}", response_model=Task)
def update_task(
    *,
    db: Session = Depends(get_db),
    task_id: str,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
):
    """Обновить задачу"""
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(
    *,
    db: Session = Depends(get_db),
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    """Удалить задачу"""
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


# Pydantic модели для bulk update
class TaskStatusUpdate(BaseModel):
    task_id: str
    status: str
    order: Optional[int] = None
    completed: Optional[bool] = None


class BulkUpdateRequest(BaseModel):
    tasks: List[TaskStatusUpdate]


class BulkUpdateResponse(BaseModel):
    updated: int
    tasks: List[Task]


@router.post("/bulk-update", response_model=BulkUpdateResponse)
def bulk_update_tasks(
    *,
    db: Session = Depends(get_db),
    bulk_request: BulkUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    """Bulk update задач (статус и порядок)"""
    updated_tasks = []
    
    for item in bulk_request.tasks:
        task = db.query(TaskModel).filter(
            TaskModel.id == item.task_id,
            TaskModel.user_id == current_user.id
        ).first()
        
        if task:
            task.status = item.status
            if item.order is not None:
                task.order = item.order
            if item.completed is not None:
                task.completed = item.completed
            updated_tasks.append(task)
    
    db.commit()
    
    # Обновляем и возвращаем задачи
    for task in updated_tasks:
        db.refresh(task)
    
    return BulkUpdateResponse(updated=len(updated_tasks), tasks=updated_tasks)
