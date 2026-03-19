from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4

from app.db.base import get_db
from app.models.event_task import EventTask
from app.models.calendar import CalendarEvent
from app.models.task import Task
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.event_task import EventTaskCreate, EventTask as EventTaskSchema
from app.schemas.task import Task as TaskSchema

router = APIRouter()


@router.post("/", response_model=EventTaskSchema)
async def add_task_to_event(
    event_task_data: EventTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Добавить задачу к событию"""
    # Проверяем существование события
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_task_data.event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    
    # Проверяем существование задачи
    task = db.query(Task).filter(
        Task.id == event_task_data.task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    # Проверяем, что связь еще не существует
    existing = db.query(EventTask).filter(
        EventTask.event_id == event_task_data.event_id,
        EventTask.task_id == event_task_data.task_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Задача уже добавлена к событию")
    
    # Создаем связь
    event_task = EventTask(
        id=str(uuid4()),
        event_id=event_task_data.event_id,
        task_id=event_task_data.task_id,
        order=event_task_data.order
    )
    
    db.add(event_task)
    db.commit()
    db.refresh(event_task)
    
    return event_task


@router.delete("/{event_id}/tasks/{task_id}")
async def remove_task_from_event(
    event_id: str,
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить задачу из события"""
    # Проверяем существование события
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    
    # Находим связь
    event_task = db.query(EventTask).filter(
        EventTask.event_id == event_id,
        EventTask.task_id == task_id
    ).first()
    
    if not event_task:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    
    db.delete(event_task)
    db.commit()
    
    return {"message": "Задача удалена из события"}


@router.get("/events/{event_id}/tasks", response_model=List[TaskSchema])
async def get_event_tasks(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить все задачи события"""
    # Проверяем существование события
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    
    # Получаем связи
    event_tasks = db.query(EventTask).filter(
        EventTask.event_id == event_id
    ).order_by(EventTask.order).all()
    
    # Получаем задачи
    task_ids = [et.task_id for et in event_tasks]
    tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
    
    # Сортируем задачи в соответствии с порядком
    task_dict = {task.id: task for task in tasks}
    sorted_tasks = [task_dict[et.task_id] for et in event_tasks if et.task_id in task_dict]
    
    return sorted_tasks


@router.post("/events/{event_id}/tasks/reorder")
async def reorder_event_tasks(
    event_id: str,
    task_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Изменить порядок задач в событии"""
    # Проверяем существование события
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    
    # Обновляем порядок
    for order, task_id in enumerate(task_ids):
        event_task = db.query(EventTask).filter(
            EventTask.event_id == event_id,
            EventTask.task_id == task_id
        ).first()
        
        if event_task:
            event_task.order = order
    
    db.commit()
    
    return {"message": "Порядок задач обновлен"}
