from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from app.db.base import get_db
from app.models.calendar import CalendarEvent
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.calendar import CalendarEventCreate, CalendarEventUpdate, CalendarEvent as CalendarEventSchema

router = APIRouter()

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
        # События которые заканчиваются после start
        query = query.filter(CalendarEvent.end > start)
    if end:
        # События которые начинаются до end (включая весь день)
        # Для событий на весь день - они должны показываться если start < end_date
        query = query.filter(CalendarEvent.start < end)
    
    events = query.order_by(CalendarEvent.start).all()
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