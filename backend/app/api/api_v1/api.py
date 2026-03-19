from fastapi import APIRouter
from app.api.api_v1.endpoints import calendar, tasks, tags, kanban, event_tasks

api_router = APIRouter()
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(kanban.router, prefix="/kanban", tags=["kanban"])
api_router.include_router(event_tasks.router, prefix="/event-tasks", tags=["event-tasks"])




