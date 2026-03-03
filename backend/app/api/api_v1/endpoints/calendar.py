from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import uuid4

from app.db.base import get_db
from app.models.calendar import CalendarEvent
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.calendar import CalendarEventCreate, CalendarEventUpdate, CalendarEvent as CalendarEventSchema

router = APIRouter()

def expand_recurring_events(events: List[CalendarEvent], start: datetime, end: datetime) -> List[dict]:
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
                expanded.append({
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'start': event.start,
                    'end': event.end,
                    'all_day': event.all_day,
                    'color': event.color,
                    'priority': event.priority,
                    'tag_id': event.tag_id,
                    'user_id': event.user_id,
                    'recurrence_type': event.recurrence_type,
                    'recurrence_days': event.recurrence_days,
                    'recurrence_end_date': event.recurrence_end_date,
                    'recurrence_count': event.recurrence_count,
                    'created_at': event.created_at,
                    'updated_at': event.updated_at,
                })
                continue
            
            # Определяем диапазон повторения
            event_start = event.start
            event_end = event.end
            duration = event_end - event_start
            
            # Начальная дата - первое вхождение события
            current_date = event_start
            
            # Если указана end_date для повторения, используем её
            recurrence_end = event.recurrence_end_date
            # Делаем даты сравниваемыми (убираем tzinfo если есть)
            if recurrence_end:
                if recurrence_end.tzinfo:
                    recurrence_end = recurrence_end.replace(tzinfo=None)
                search_start = start.replace(tzinfo=None) if start.tzinfo else start
                search_end = end.replace(tzinfo=None) if end.tzinfo else end
                current_date_cmp = current_date.replace(tzinfo=None) if current_date.tzinfo else current_date
                
                if recurrence_end < search_start:
                    continue
            else:
                search_start = start.replace(tzinfo=None) if start.tzinfo else start
                search_end = end.replace(tzinfo=None) if end.tzinfo else end
                current_date_cmp = current_date.replace(tzinfo=None) if current_date.tzinfo else current_date
            
            # Если есть ограничение по количеству повторений
            max_occurrences = event.recurrence_count
            
            occurrence_count = 0
            
            while current_date_cmp <= search_end:
                # Проверяем, попадает ли это вхождение в запрошенный период
                if current_date_cmp >= search_start and current_date_cmp <= search_end:
                    # Проверяем день недели (0=понедельник, 6=воскресенье)
                    weekday = current_date_cmp.weekday()
                    if weekday in recurrence_days:
                        # Создаём словарь с данными события
                        expanded.append({
                            'id': f"{event.id}_{occurrence_count}",
                            'original_id': event.id,  # Оригинальный ID для edit/delete
                            'title': event.title,
                            'description': event.description,
                            'start': current_date,
                            'end': current_date + duration,
                            'all_day': event.all_day,
                            'color': event.color,
                            'priority': event.priority,
                            'tag_id': event.tag_id,
                            'user_id': event.user_id,
                            'recurrence_type': event.recurrence_type,
                            'recurrence_days': event.recurrence_days,
                            'recurrence_end_date': event.recurrence_end_date,
                            'recurrence_count': event.recurrence_count,
                            'created_at': event.created_at,
                            'updated_at': event.updated_at,
                        })
                        
                        if max_occurrences and occurrence_count >= max_occurrences - 1:
                            break
                
                # Переходим к следующей неделе
                current_date += timedelta(days=7)
                current_date_cmp = current_date.replace(tzinfo=None) if current_date.tzinfo else current_date
                occurrence_count += 1
                
                # Защита от бесконечного цикла
                if occurrence_count > 365:  # Максимум год повторений
                    break
                
                # Проверяем выход за пределы end_date повторения
                if recurrence_end and current_date_cmp > recurrence_end:
                    break
        else:
            # Обычное событие без повторения
            expanded.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'start': event.start,
                'end': event.end,
                'all_day': event.all_day,
                'color': event.color,
                'priority': event.priority,
                'tag_id': event.tag_id,
                'user_id': event.user_id,
                'recurrence_type': event.recurrence_type,
                'recurrence_days': event.recurrence_days,
                'recurrence_end_date': event.recurrence_end_date,
                'recurrence_count': event.recurrence_count,
                'created_at': event.created_at,
                'updated_at': event.updated_at,
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
    if start:
        query = query.filter(CalendarEvent.end > start)
    if end:
        from datetime import timedelta
        end_inclusive = end + timedelta(days=1)
        query = query.filter(CalendarEvent.start < end_inclusive)
    
    events = query.order_by(CalendarEvent.start).all()
    
    # Разворачиваем повторяющиеся события
    if start and end:
        events = expand_recurring_events(events, start, end)
    
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
    
    update_data = event_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
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