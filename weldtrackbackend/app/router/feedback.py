from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db import get_db
from app.models.feedback import Feedback
from app.models.user import User, UserRole
from app.models.feedback_interactions import FeedbackComment, FeedbackLike
from app.router.auth import get_current_user
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackResponse
from app.schemas.feedback_interactions import FeedbackCommentCreate, FeedbackCommentResponse

router = APIRouter(prefix="/feedbacks", tags=["feedbacks"])


# ... (ensure_customer_feedback_owner unchanged)


@router.get("", response_model=list[FeedbackResponse])
def list_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all feedbacks with user profile images, comments and likes"""
    query = (
        select(Feedback)
        .order_by(desc(Feedback.date))
        .offset(skip)
        .limit(limit)
    )
    feedbacks = db.scalars(query).all()
    
    response = []
    for feedback in feedbacks:
        feedback_data = FeedbackResponse.model_validate(feedback)
        # Fetch user profile image
        user = db.scalar(select(User).filter(User.email == feedback.email))
        if user:
            feedback_data.profile_image = user.profile_image
        response.append(feedback_data)
        
    return response

# ... (other routes: get_feedback, create_feedback, update_feedback, delete_feedback)


@router.post("/{feedback_id}/comments", response_model=FeedbackCommentResponse)
def add_comment(
    feedback_id: int,
    payload: FeedbackCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a comment to feedback"""
    feedback = db.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    
    comment = FeedbackComment(
        feedback_id=feedback_id,
        user_email=current_user.email,
        comment=payload.comment
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.post("/{feedback_id}/likes", status_code=status.HTTP_201_CREATED)
def toggle_like(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle a like on feedback"""
    feedback = db.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    
    like = db.scalar(select(FeedbackLike).filter_by(feedback_id=feedback_id, user_email=current_user.email))
    if like:
        db.delete(like)
    else:
        new_like = FeedbackLike(feedback_id=feedback_id, user_email=current_user.email)
        db.add(new_like)
        
    db.commit()
    return {"message": "Like toggled"}


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
