from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

# Database and session
from cx360.backend.database import get_db

# Models and Schemas
from cx360.backend.models.feedback import Feedback, FeedbackCreate, FeedbackUpdate, FeedbackResponse
from cx360.backend.models.user import User as UserModel # SQLAlchemy User model
# Auth dependencies
from cx360.backend.routes.auth import get_current_active_user # Adjusted import path

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
    # dependencies=[Depends(get_current_active_user)] # Optional: protect all feedback routes
)

# Placeholder for CRUD operations / helper functions
# These can be moved to a separate crud_feedback.py file later for better organization

def db_create_feedback(db: Session, feedback_in: FeedbackCreate, user_id: Optional[int] = None) -> Feedback:
    db_feedback = Feedback(**feedback_in.model_dump(exclude_unset=True)) # Use model_dump for Pydantic v2
    if user_id:
        db_feedback.user_id = user_id
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def db_get_feedback(db: Session, feedback_id: int) -> Optional[Feedback]:
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()

def db_get_all_feedback(db: Session, skip: int = 0, limit: int = 100) -> List[Feedback]:
    return db.query(Feedback).offset(skip).limit(limit).all()

def db_update_feedback(db: Session, feedback_id: int, feedback_in: FeedbackUpdate, current_user: UserModel) -> Optional[Feedback]:
    db_feedback = db_get_feedback(db, feedback_id)
    if not db_feedback:
        return None

    # Authorization check: Only owner or admin can update (Example)
    # For this, you might need to define roles in your User model and check current_user.role
    # For now, let's assume if user_id is present, only that user can update.
    # This is a simplified check. A more robust system would involve roles/permissions.
    if db_feedback.user_id is not None and db_feedback.user_id != current_user.id:
         # Or if current_user.role != "admin" (pseudo-code for role check)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this feedback")

    update_data = feedback_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_feedback, key, value)

    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def db_delete_feedback(db: Session, feedback_id: int, current_user: UserModel) -> Optional[Feedback]:
    db_feedback = db_get_feedback(db, feedback_id)
    if not db_feedback:
        return None

    # Authorization check (similar to update)
    if db_feedback.user_id is not None and db_feedback.user_id != current_user.id:
        # Or if current_user.role != "admin"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this feedback")

    db.delete(db_feedback)
    db.commit()
    return db_feedback # Return the deleted object for confirmation, or just True

# --- CRUD Endpoints ---

# Create Feedback
@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Optional[UserModel] = Depends(get_current_active_user) # Make current_user optional
):
    # If current_user is None and feedback_in.user_id is also None, it's anonymous
    # If current_user is provided, we can link the feedback to this user
    user_id_to_set = None
    if current_user:
        user_id_to_set = current_user.id
    elif feedback_in.user_id: # Allow specifying user_id if not logged in (e.g. by admin)
        # Potentially add a check here: only admins can set user_id for others
        user_id_to_set = feedback_in.user_id

    # To ensure feedback_in.user_id (if present in body) is not overriding current_user.id unless intended
    if current_user and feedback_in.user_id and feedback_in.user_id != current_user.id:
        # This case might need clarification: if logged in user specifies different user_id
        # For now, prioritize current_user.id if logged in.
        # Or raise HTTPException if admin role is not present
        pass # Assuming current_user's ID should be authoritative if logged in.

    created_feedback = db_create_feedback(db=db, feedback_in=feedback_in, user_id=user_id_to_set)
    return created_feedback

# Read One Feedback
@router.get("/{feedback_id}", response_model=FeedbackResponse)
def read_feedback(feedback_id: int, db: Session = Depends(get_db)):
    db_feedback = db_get_feedback(db, feedback_id=feedback_id)
    if db_feedback is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    return db_feedback

# Read Multiple Feedback
@router.get("/", response_model=List[FeedbackResponse])
def read_all_feedback(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    feedbacks = db_get_all_feedback(db, skip=skip, limit=limit)
    return feedbacks

# Update Feedback
@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    feedback_id: int,
    feedback_in: FeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user) # Require authentication
):
    updated_feedback = db_update_feedback(db, feedback_id, feedback_in, current_user)
    if updated_feedback is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found or not authorized to update")
    return updated_feedback

# Delete Feedback
@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user) # Require authentication
):
    deleted_feedback = db_delete_feedback(db, feedback_id, current_user)
    if deleted_feedback is None:
        # This means either not found or not authorized by the check in db_delete_feedback
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found or not authorized to delete")
    return # FastAPI will return 204 No Content
