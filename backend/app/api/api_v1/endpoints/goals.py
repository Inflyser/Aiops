from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4

from app.db.base import get_db
from app.models.goal import Goal
from app.models.user import User
from app.core.security import get_current_user
from app.schemas.goal import GoalCreate, GoalUpdate, Goal as GoalSchema

router = APIRouter()

@router.get("/", response_model=List[GoalSchema])
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить все цели пользователя"""
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).order_by(Goal.order).all()
    return goals

@router.post("/", response_model=GoalSchema, status_code=201)
def create_goal(
    *,
    db: Session = Depends(get_db),
    goal_in: GoalCreate,
    current_user: User = Depends(get_current_user),
):
    goal = Goal(
        id=str(uuid4()),
        title=goal_in.title,
        description=goal_in.description,
        status=goal_in.status,
        goal_type=goal_in.goal_type,
        target_value=goal_in.target_value,
        target_unit=goal_in.target_unit,
        current_value=goal_in.current_value,
        deadline=goal_in.deadline,
        icon=goal_in.icon,
        is_featured=goal_in.is_featured,
        featured_position=goal_in.featured_position,
        order=goal_in.order,
        user_id=current_user.id
    )

    max_order = db.query(Goal.order).filter(
        Goal.user_id == current_user.id
    ).order_by(Goal.order.desc()).first()
    goal.order = (max_order[0] + 1) if max_order and max_order[0] is not None else 0

    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

@router.put("/{goal_id}", response_model=GoalSchema)
def update_goal(
    *,
    db: Session = Depends(get_db),
    goal_id: str,
    goal_in: GoalUpdate,
    current_user: User = Depends(get_current_user),
):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    update_data = goal_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(goal, field, value)

    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/{goal_id}")
def delete_goal(
    *,
    db: Session = Depends(get_db),
    goal_id: str,
    current_user: User = Depends(get_current_user),
):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted", "id": goal_id}
