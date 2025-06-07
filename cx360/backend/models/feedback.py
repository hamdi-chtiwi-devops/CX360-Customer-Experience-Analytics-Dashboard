from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float # Added Float
from sqlalchemy.orm import relationship
from datetime import datetime
from cx360.backend.database import Base # Adjusted import path
from pydantic import BaseModel
from typing import Optional

# SQLAlchemy Model for Feedback
class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    rating = Column(Integer, nullable=True) # Could add CheckConstraint('rating >= 1 AND rating <= 5')
    feedback_text = Column(Text, nullable=False)
    source = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    submitter = relationship("User", back_populates="feedbacks")

    # New sentiment fields
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(20), nullable=True) # e.g., "positive", "negative", "neutral"

# Pydantic Schemas for Feedback
class FeedbackBase(BaseModel):
    customer_name: Optional[str] = None
    email: Optional[str] = None
    rating: Optional[int] = None
    feedback_text: str
    source: Optional[str] = None
    user_id: Optional[int] = None # For request, if submitted by a specific user

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    customer_name: Optional[str] = None
    email: Optional[str] = None
    rating: Optional[int] = None
    feedback_text: Optional[str] = None
    source: Optional[str] = None

class FeedbackResponse(FeedbackBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None # Ensure updated_at is optional if it can be null
    # user_id is already in FeedbackBase and thus inherited.

    # New sentiment fields for response
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None

    class Config:
        from_attributes = True # Pydantic V2 (formerly orm_mode)

# Pydantic Model for CSV Row Validation
from pydantic import conint, constr # Already have BaseModel, EmailStr, Optional, datetime

class FeedbackCsvRow(BaseModel):
    customer_name: Optional[str] = None
    email: Optional[EmailStr] = None
    rating: conint(ge=1, le=5) # Assuming 1-5 rating scale
    feedback_text: constr(min_length=1)
    source: Optional[str] = None
    # Pydantic will try to parse common datetime strings.
    # For specific formats, custom validator or pre-parsing might be needed.
    created_at: Optional[datetime] = None
