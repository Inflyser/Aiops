from fastapi import APIRouter
from app.api.api_v1.endpoints import calendar, tasks

api_router = APIRouter()
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])




