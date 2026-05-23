from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import uuid4

from app.db.base import get_db
from app.models.calendar import CalendarEvent
from app.models.event_task import EventTask
from app.models.task import Task
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.calendar import CalendarEventCreate, CalendarEventUpdate, CalendarEvent as CalendarEventSchema

router = APIRouter()


def get_event_tasks_info(db: Session, event_id: str) -> dict:
    """Получить информацию о задачах события"""
    event_tasks = db.query(EventTask).filter(
        EventTask.event_id == event_id
    ).order_by(EventTask.order).all()
    
    task_ids = [et.task_id for et in event_tasks]
    
    # Получаем задачи, чтобы подсчитать выполненные
    if task_ids:
        tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
        completed_task_count = sum(1 for task in tasks if task.completed)
    else:
        completed_task_count = 0
    
    return {
        'task_ids': task_ids,
        'task_count': len(task_ids),
        'completed_task_count': completed_task_count
    }

def expand_recurring_events(events: List[CalendarEvent], start: datetime, end: datetime, db: Session) -> List[dict]:
    """Развернуть повторяющиеся события в отдельные экземпляры"""
    expanded = []
    
    for event in events:
        if event.recurrence_type == 'weekly' and event.recurrence_days:
            # Получаем дни недели из строки "0,2,4"
            try:
                recurrence_days = [int(d) for d in event.recurrence_days.split(',') if d]
            except:
                recurrence_days = []
            
            if not recurrence_days:
                tasks_info = get_event_tasks_info(db, event.id)
                expanded.append({
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'start': event.start,
                    'end': event.end,
                    'all_day': event.all_day,
                    'color': event.color,
                    'priority': event.priority,
                    'is_important': event.is_important,
                    'tag_id': event.tag_id,
                    'user_id': event.user_id,
                    'recurrence_type': event.recurrence_type,
                    'recurrence_days': event.recurrence_days,
                    'recurrence_end_date': event.recurrence_end_date,
                    'recurrence_count': event.recurrence_count,
                    'created_at': event.created_at,
                    'updated_at': event.updated_at,
                    'task_ids': tasks_info['task_ids'],
                    'task_count': tasks_info['task_count'],
                    'completed_task_count': tasks_info['completed_task_count'],
                })
                continue
            
            # Определяем диапазон повторения
            event_start = event.start
            event_end = event.end
            duration = event_end - event_start
            
            event_start_cmp = event_start.replace(tzinfo=None) if event_start.tzinfo else event_start
            
            # Если указана end_date для повторения, используем её
            recurrence_end = event.recurrence_end_date
            if recurrence_end:
                recurrence_end = recurrence_end.replace(tzinfo=None) if recurrence_end.tzinfo else recurrence_end
            
            search_start = start.replace(tzinfo=None) if start.tzinfo else start
            search_end = end.replace(tzinfo=None) if end.tzinfo else end
            
            if recurrence_end and recurrence_end < search_start:
                continue
            
            # Если есть ограничение по количеству повторений
            max_occurrences = event.recurrence_count
            
            occurrence_count = 0
            
            # Начинаем с понедельника недели, в которую попадает событие
            start_of_week = event_start_cmp - timedelta(days=event_start_cmp.weekday())
            current_week_start = start_of_week
            
            while True:
                for day_idx in recurrence_days:
                    # Дата конкретного дня в текущей неделе
                    occurrence_date = current_week_start + timedelta(days=day_idx)
                    
                    # Не раньше даты начала события
                    if occurrence_date < event_start_cmp:
                        continue
                    
                    # Не позже даты окончания повторения
                    if recurrence_end and occurrence_date > recurrence_end:
                        continue
                    
                    # Не позже запрошенного периода
                    if occurrence_date > search_end:
                        continue
                    
                    # Проверяем, попадает ли в запрошенный период
                    if occurrence_date >= search_start:
                        # Создаём вхождение в указанную дату со временем из события
                        occurrence_datetime = event_start.replace(
                            year=occurrence_date.year,
                            month=occurrence_date.month,
                            day=occurrence_date.day
                        )
                        
                        tasks_info = get_event_tasks_info(db, event.id)
                        expanded.append({
                            'id': f"{event.id}_{occurrence_count}",
                            'original_id': event.id,
                            'title': event.title,
                            'description': event.description,
                            'start': occurrence_datetime,
                            'end': occurrence_datetime + duration,
                            'all_day': event.all_day,
                            'color': event.color,
                            'priority': event.priority,
                            'is_important': event.is_important,
                            'tag_id': event.tag_id,
                            'user_id': event.user_id,
                            'recurrence_type': event.recurrence_type,
                            'recurrence_days': event.recurrence_days,
                            'recurrence_end_date': event.recurrence_end_date,
                            'recurrence_count': event.recurrence_count,
                            'task_ids': tasks_info['task_ids'],
                            'task_count': tasks_info['task_count'],
                            'completed_task_count': tasks_info['completed_task_count'],
                            'created_at': event.created_at,
                            'updated_at': event.updated_at,
                        })
                        occurrence_count += 1
                        
                        if max_occurrences and occurrence_count >= max_occurrences:
                            break
                
                if max_occurrences and occurrence_count >= max_occurrences:
                    break
                
                # Переходим к следующей неделе
                current_week_start += timedelta(days=7)
                
                # Защита от бесконечного цикла
                if occurrence_count > 365:
                    break
                
                # Проверяем выход за пределы end_date повторения
                if recurrence_end and current_week_start > recurrence_end:
                    break
                
                # Выходим, если ушли слишком далеко за search_end
                if current_week_start > search_end + timedelta(days=7):
                    break
            
            # Добавляем оригинальное событие, если его день не входит в выбранные дни повторения
            # (иначе оно уже есть среди расширенных экземпляров)
            if event_start_cmp.weekday() not in recurrence_days:
                tasks_info = get_event_tasks_info(db, event.id)
                expanded.append({
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'start': event.start,
                    'end': event.end,
                    'all_day': event.all_day,
                    'color': event.color,
                    'priority': event.priority,
                    'is_important': event.is_important,
                    'tag_id': event.tag_id,
                    'user_id': event.user_id,
                    'recurrence_type': event.recurrence_type,
                    'recurrence_days': event.recurrence_days,
                    'recurrence_end_date': event.recurrence_end_date,
                    'recurrence_count': event.recurrence_count,
                    'created_at': event.created_at,
                    'updated_at': event.updated_at,
                    'task_ids': tasks_info['task_ids'],
                    'task_count': tasks_info['task_count'],
                    'completed_task_count': tasks_info['completed_task_count'],
                })
        else:
            # Обычное событие без повторения
            tasks_info = get_event_tasks_info(db, event.id)
            expanded.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'start': event.start,
                'end': event.end,
                'all_day': event.all_day,
                'color': event.color,
                'priority': event.priority,
                'is_important': event.is_important,
                'tag_id': event.tag_id,
                'user_id': event.user_id,
                'recurrence_type': event.recurrence_type,
                'recurrence_days': event.recurrence_days,
                'recurrence_end_date': event.recurrence_end_date,
                'recurrence_count': event.recurrence_count,
                'created_at': event.created_at,
                'updated_at': event.updated_at,
                'task_ids': tasks_info['task_ids'],
                'task_count': tasks_info['task_count'],
                'completed_task_count': tasks_info['completed_task_count'],
            })
    
    return expanded

@router.get("/", response_model=List[CalendarEventSchema])
def get_calendar_events(
    db: Session = Depends(get_db),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Получить события календаря"""
    query = db.query(CalendarEvent).filter(CalendarEvent.user_id == current_user.id)
    
    # Показываем события которые пересекаются с запрошенным периодом
    # Для повторяющихся событий также учитываем их рекуррентный диапазон
    if start:
        query = query.filter(
            or_(
                CalendarEvent.end > start,
                and_(
                    CalendarEvent.recurrence_type.isnot(None),
                    or_(
                        CalendarEvent.recurrence_end_date.is_(None),
                        CalendarEvent.recurrence_end_date > start
                    )
                )
            )
        )
    if end:
        from datetime import timedelta
        end_inclusive = end + timedelta(days=1)
        query = query.filter(CalendarEvent.start < end_inclusive)
    
    events = query.order_by(CalendarEvent.start).all()
    
    # Разворачиваем повторяющиеся события
    if start and end:
        events = expand_recurring_events(events, start, end, db)
    
    return events

@router.post("/", response_model=CalendarEventSchema, status_code=201)
def create_calendar_event(
    *,
    db: Session = Depends(get_db),
    event_in: CalendarEventCreate,
    current_user: User = Depends(get_current_user),
):
    """Создать событие календаря"""
    event_data = event_in.model_dump()
    event_data["id"] = str(uuid4())
    event_data["user_id"] = current_user.id
    
    event = CalendarEvent(**event_data)
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Добавляем информацию о задачах
    tasks_info = get_event_tasks_info(db, event.id)
    event.task_ids = tasks_info['task_ids']
    event.task_count = tasks_info['task_count']
    event.completed_task_count = tasks_info['completed_task_count']
    
    return event

@router.put("/{event_id}", response_model=CalendarEventSchema)
def update_calendar_event(
    *,
    db: Session = Depends(get_db),
    event_id: str,
    event_in: CalendarEventUpdate,
    current_user: User = Depends(get_current_user),
):
    """Обновить событие календаря"""
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event_in.model_dump(exclude_unset=True, exclude={'is_important'})
    
    for field, value in update_data.items():
        setattr(event, field, value)
    
    # Handle is_important separately
    if event_in.is_important is not None:
        event.is_important = event_in.is_important
    
    db.commit()
    db.refresh(event)
    
    # Добавляем информацию о задачах
    tasks_info = get_event_tasks_info(db, event.id)
    event.task_ids = tasks_info['task_ids']
    event.task_count = tasks_info['task_count']
    event.completed_task_count = tasks_info['completed_task_count']
    
    return event

@router.delete("/{event_id}")
def delete_calendar_event(
    *,
    db: Session = Depends(get_db),
    event_id: str,
    current_user: User = Depends(get_current_user),
):
    """Удалить событие календаря"""
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    return {"message": "Event deleted", "id": event_id}