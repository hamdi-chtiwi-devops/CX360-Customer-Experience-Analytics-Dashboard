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
