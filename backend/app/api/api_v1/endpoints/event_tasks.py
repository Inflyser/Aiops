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
    """Добавить задачу к событию (создаёт копию задачи из шаблона или новую задачу по названию)"""
    # Проверяем существование события
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_task_data.event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    
    # Если передан title (quick-add), создаём новую задачу напрямую
    if event_task_data.title:
        task_copy = Task(
            id=str(uuid4()),
            title=event_task_data.title,
            description='',
            completed=False,
            status='event',
            priority=None,
            tags=[],
            order=0,
            user_id=current_user.id,
        )
        db.add(task_copy)
        db.flush()
    else:
        # Находим шаблон задачи в Inbox
        template = db.query(Task).filter(
            Task.id == event_task_data.task_id,
            Task.user_id == current_user.id
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Задача-шаблон не найдена")
        
        # Создаём НОВУЮ независимую копию задачи с теми же данными
        task_copy = Task(
            id=str(uuid4()),
            title=template.title,
            description=template.description,
            completed=False,
            status='event',
            priority=template.priority,
            tags=template.tags,
            order=0,
            user_id=current_user.id,
        )
        db.add(task_copy)
        db.flush()
    
    # Создаём связь между новой задачей и событием
    event_task = EventTask(
        id=str(uuid4()),
        event_id=event_task_data.event_id,
        task_id=task_copy.id,
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
    """Удалить задачу из события (удаляет копию задачи, шаблон в Inbox остаётся)"""
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
    
    # Находим и удаляем копию задачи (она создавалась специально для события)
    task_copy = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if task_copy:
        db.delete(task_copy)
    
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


@router.post("/add-category-to-event", response_model=dict)
async def add_category_to_event(
    event_id: str,
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Добавить все задачи категории к событию (создаёт копии задач-шаблонов)"""
    # Проверяем существование события
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    
    # Получаем задачи категории (шаблоны)
    category_tasks = db.query(Task).filter(
        Task.column_id == category_id,
        Task.user_id == current_user.id
    ).all()
    
    # Создаём копии задач и привязываем к событию
    for i, template in enumerate(category_tasks):
        task_copy = Task(
            id=str(uuid4()),
            title=template.title,
            description=template.description,
            completed=False,
            status='event',
            priority=template.priority,
            tags=template.tags,
            order=0,
            user_id=current_user.id,
        )
        db.add(task_copy)
        db.flush()
        
        event_task = EventTask(
            id=str(uuid4()),
            event_id=event_id,
            task_id=task_copy.id,
            order=i
        )
        db.add(event_task)
    
    db.commit()
    
    return {
        "message": f"Создано и добавлено {len(category_tasks)} задач к событию"
    }
