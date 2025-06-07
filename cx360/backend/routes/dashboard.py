from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from cx360.backend.database import get_db
from cx360.backend.models.feedback import Feedback as FeedbackModel
# Assuming UserResponse is the Pydantic model for user details from your auth routes
# If User is the SQLAlchemy model, you might need to adjust, but get_current_active_user should return the Pydantic model.
from cx360.backend.models.user import UserResponse
from cx360.backend.routes.auth import get_current_active_user # Adjusted import path
from pydantic import BaseModel

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard KPIs"], # Changed tag for clarity
    dependencies=[Depends(get_current_active_user)] # Protect all routes in this router
)

class KpiResponse(BaseModel):
    total_feedback: int
    average_rating: Optional[float] = None

# --- Pydantic Models for Chart Data ---
from datetime import date # Add this import
from typing import List # Add this import

class FeedbackCountOverTimePoint(BaseModel):
    date: date
    count: int

class FeedbackCountOverTimeResponse(BaseModel):
    data: List[FeedbackCountOverTimePoint]

class RatingDistributionPoint(BaseModel):
    rating: int # Assuming rating is stored as integer
    count: int

class RatingDistributionResponse(BaseModel):
    data: List[RatingDistributionPoint]


@router.get("/kpis", response_model=KpiResponse)
async def get_dashboard_kpis(db: Session = Depends(get_db), current_user: UserResponse = Depends(get_current_active_user)):
    # current_user is injected by Depends(get_current_active_user) but not directly used in this specific KPI calculation.
    # It's good practice to keep it if other /dashboard endpoints might need user-specific data.

    total_feedback = db.query(func.count(FeedbackModel.id)).scalar()

    # Query for average rating. func.avg might return Decimal, None, or float.
    avg_rating_query_result = db.query(func.avg(FeedbackModel.rating)).scalar()

    average_rating: Optional[float] = None
    if avg_rating_query_result is not None:
        try:
            average_rating = float(avg_rating_query_result)
        except TypeError:
            # This handles cases where it might be a non-convertible type, though unlikely for avg.
            average_rating = None

    return KpiResponse(
        total_feedback=total_feedback if total_feedback is not None else 0,
        average_rating=average_rating
    )

# --- Endpoint for Feedback Count Over Time ---
from sqlalchemy import cast, Date as SQLDate # Add these specific imports
from datetime import timedelta # Already have 'date' from Pydantic models section

@router.get("/kpis/feedback-over-time", response_model=FeedbackCountOverTimeResponse)
async def get_feedback_count_over_time(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user) # Endpoint is protected
):
    thirty_days_ago = date.today() - timedelta(days=30)

    query_result = (
        db.query(
            cast(FeedbackModel.created_at, SQLDate).label("feedback_date"),
            func.count(FeedbackModel.id).label("feedback_count")
        )
        .filter(cast(FeedbackModel.created_at, SQLDate) >= thirty_days_ago)
        .group_by(cast(FeedbackModel.created_at, SQLDate))
        .order_by(cast(FeedbackModel.created_at, SQLDate))
        .all()
    )

    # Convert query result (list of Row objects) to list of Pydantic models
    data_points = [
        FeedbackCountOverTimePoint(date=row.feedback_date, count=row.feedback_count)
        for row in query_result
    ]

    return FeedbackCountOverTimeResponse(data=data_points)

# --- Endpoint for Rating Distribution ---
@router.get("/kpis/rating-distribution", response_model=RatingDistributionResponse)
async def get_rating_distribution(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user) # Endpoint is protected
):
    query_result = (
        db.query(
            FeedbackModel.rating.label("rating_value"),
            func.count(FeedbackModel.id).label("rating_count")
        )
        .filter(FeedbackModel.rating.isnot(None)) # Only include feedback with a rating
        .group_by(FeedbackModel.rating)
        .order_by(FeedbackModel.rating)
        .all()
    )

    data_points = [
        RatingDistributionPoint(rating=row.rating_value, count=row.rating_count)
        for row in query_result if row.rating_value is not None # Ensure rating_value itself isn't None after query
    ]

    return RatingDistributionResponse(data=data_points)
