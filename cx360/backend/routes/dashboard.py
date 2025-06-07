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

class SentimentDistributionPoint(BaseModel):
    label: str
    count: int

class SentimentDistributionResponse(BaseModel):
    data: List[SentimentDistributionPoint]


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
from sqlalchemy import cast, Date as SQLDate
from datetime import timedelta, date as py_date # Renamed to avoid conflict with Pydantic's date
from fastapi import Query # For query parameter descriptions and validation

@router.get("/kpis/feedback-over-time", response_model=FeedbackCountOverTimeResponse)
async def get_feedback_count_over_time(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user), # Endpoint is protected
    start_date: Optional[py_date] = Query(None, description="Start date (YYYY-MM-DD) for filtering feedback. Defaults to 30 days ago if end_date is also None."),
    end_date: Optional[py_date] = Query(None, description="End date (YYYY-MM-DD) for filtering feedback. Defaults to today if start_date is also None.")
):
    # Determine effective date range
    effective_start_date: py_date
    effective_end_date: py_date

    if start_date is None and end_date is None:
        # Default: last 30 days
        effective_end_date = py_date.today()
        effective_start_date = effective_end_date - timedelta(days=29) # Inclusive 30 days
    elif start_date is None:
        # Only end_date is provided: default start_date to 30 days before end_date
        effective_end_date = end_date
        effective_start_date = effective_end_date - timedelta(days=29)
    elif end_date is None:
        # Only start_date is provided: default end_date to today
        effective_start_date = start_date
        effective_end_date = py_date.today()
    else:
        # Both start_date and end_date are provided
        effective_start_date = start_date
        effective_end_date = end_date

    if effective_start_date > effective_end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date.")

    query = (
        db.query(
            cast(FeedbackModel.created_at, SQLDate).label("feedback_date"),
            func.count(FeedbackModel.id).label("feedback_count")
        )
        .filter(cast(FeedbackModel.created_at, SQLDate) >= effective_start_date)
        .filter(cast(FeedbackModel.created_at, SQLDate) <= effective_end_date)
        .group_by(cast(FeedbackModel.created_at, SQLDate))
        .order_by(cast(FeedbackModel.created_at, SQLDate))
    )

    query_result = query.all()

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
    current_user: UserResponse = Depends(get_current_active_user), # Endpoint is protected
    start_date: Optional[py_date] = Query(None, description="Start date (YYYY-MM-DD) to filter ratings. If provided, end_date should also be considered or defaults to today."),
    end_date: Optional[py_date] = Query(None, description="End date (YYYY-MM-DD) to filter ratings. If provided, start_date should also be considered or defaults to a very early date.")
):
    query = (
        db.query(
            FeedbackModel.rating.label("rating_value"),
            func.count(FeedbackModel.id).label("rating_count")
        )
        .filter(FeedbackModel.rating.isnot(None)) # Only include feedback with a rating
    )

    # Apply date filters if provided
    if start_date and end_date:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date cannot be after end date.")
        query = query.filter(cast(FeedbackModel.created_at, SQLDate) >= start_date)
        query = query.filter(cast(FeedbackModel.created_at, SQLDate) <= end_date)
    elif start_date: # Only start_date is provided
        query = query.filter(cast(FeedbackModel.created_at, SQLDate) >= start_date)
        # Optionally, could default end_date to today, or require both if one is given.
        # For rating distribution, perhaps filtering from start_date to infinity (or today) is fine.
        # Let's assume if only start_date, it's from start_date until now.
        query = query.filter(cast(FeedbackModel.created_at, SQLDate) <= py_date.today())
    elif end_date: # Only end_date is provided
        query = query.filter(cast(FeedbackModel.created_at, SQLDate) <= end_date)
        # If only end_date, filter up to that date from the beginning of time.
        # No specific start_date filter needed in this case beyond what's already in the query.

    query_result = query.group_by(FeedbackModel.rating).order_by(FeedbackModel.rating).all()

    data_points = [
        RatingDistributionPoint(rating=row.rating_value, count=row.rating_count)
        for row in query_result if row.rating_value is not None # Ensure rating_value itself isn't None after query
    ]

    return RatingDistributionResponse(data=data_points)

# --- Endpoint for Sentiment Distribution ---
@router.get("/kpis/sentiment-distribution", response_model=SentimentDistributionResponse)
async def get_sentiment_distribution(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user), # Endpoint is protected
    start_date: Optional[py_date] = Query(None, description="Start date (YYYY-MM-DD) to filter sentiment distribution."),
    end_date: Optional[py_date] = Query(None, description="End date (YYYY-MM-DD) to filter sentiment distribution.")
):
    query = (
        db.query(
            FeedbackModel.sentiment_label,
            func.count(FeedbackModel.id).label("count")
        )
        .filter(FeedbackModel.sentiment_label.isnot(None)) # Only include feedback with a sentiment label
        .filter(FeedbackModel.sentiment_label != "") # Also filter out empty strings if they can occur
    )

    # Apply date filters if provided
    if start_date and end_date:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date cannot be after end date.")
        query = query.filter(cast(FeedbackModel.created_at, SQLDate) >= start_date)
        query = query.filter(cast(FeedbackModel.created_at, SQLDate) <= end_date)
    elif start_date: # Only start_date is provided
        query = query.filter(cast(FeedbackModel.created_at, SQLDate) >= start_date)
        query = query.filter(cast(FeedbackModel.created_at, SQLDate) <= py_date.today()) # Default end to today
    elif end_date: # Only end_date is provided
        query = query.filter(cast(FeedbackModel.created_at, SQLDate) <= end_date)
        # No specific start_date filter needed (from beginning of time up to end_date)

    query_result = query.group_by(FeedbackModel.sentiment_label).all()

    response_data = [
        SentimentDistributionPoint(label=row.sentiment_label, count=row.count)
        for row in query_result if row.sentiment_label # Ensure label is not None from query itself
    ]

    return SentimentDistributionResponse(data=response_data)

# --- Endpoint for Recommendations ---
from cx360.backend.services.recommendation_service import generate_recommendations

class RecommendationsResponse(BaseModel):
    recommendations: List[str]

@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_dashboard_recommendations(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_active_user) # Protected endpoint
):
    # The generate_recommendations function is synchronous, so no await needed here.
    # If it were async, this endpoint would need to be async and use await.
    # The current generate_recommendations calls alert_service.check_for_recent_negative_feedback_alert,
    # which is synchronous. If alert_service becomes async (e.g., for async email),
    # then generate_recommendations would also need to be async, and this endpoint too.
    # For now, all involved services are synchronous.

    recommendations_list = generate_recommendations(db)

    return RecommendationsResponse(recommendations=recommendations_list)
