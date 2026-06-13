from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db import get_db
from app.models.feedback import Feedback
from app.models.user import User, UserRole
from app.router.user.auth import get_current_user
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackResponse

router = APIRouter(prefix="/api/feedbacks", tags=["feedbacks"])


def ensure_customer_feedback_owner(feedback: Feedback, current_user: User) -> None:
    if current_user.role != UserRole.customer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can modify feedback",
        )

    if (feedback.email or "").lower() != (current_user.email or "").lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own feedback",
        )


@router.get("", response_model=list[FeedbackResponse])
def list_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all feedbacks"""
    query = select(Feedback).order_by(desc(Feedback.date)).offset(skip).limit(limit)
    feedbacks = db.scalars(query).all()
    return feedbacks


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific feedback by ID"""
    feedback = db.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    return feedback


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
):
    """Create a new feedback"""
    payload_data = payload.model_dump()
    fallback_name = payload_data.get("email", "")
    feedback = Feedback(customer_name=fallback_name, **payload_data)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    feedback_id: int,
    payload: FeedbackUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a feedback"""
    feedback = db.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    ensure_customer_feedback_owner(feedback, current_user)
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(feedback, key):
            setattr(feedback, key, value)
    
    db.commit()
    db.refresh(feedback)
    return feedback


@router.patch("/{feedback_id}", response_model=FeedbackResponse)
def partial_update_feedback(
    feedback_id: int,
    payload: FeedbackUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Partially update a feedback"""
    feedback = db.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    ensure_customer_feedback_owner(feedback, current_user)
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(feedback, key):
            setattr(feedback, key, value)
    
    db.commit()
    db.refresh(feedback)
    return feedback


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a feedback"""
    feedback = db.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    ensure_customer_feedback_owner(feedback, current_user)
    
    db.delete(feedback)
    db.commit()
