from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date as SQLDate
from datetime import date, datetime, time # Ensure all datetime components are imported
from typing import Dict, Any
import logging

from cx360.backend.models.feedback import Feedback as FeedbackModel # Ensure correct alias if any

logger = logging.getLogger(__name__)
# Ensure logger is configured, e.g., by basicConfig in main or if this service is part of a larger app
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


def generate_daily_summary_report(db: Session, report_date: date) -> Dict[str, Any]:
    """
    Generates a daily summary report for feedback received on a specific date.

    Args:
        db: The SQLAlchemy database session.
        report_date: The date for which to generate the report.

    Returns:
        A dictionary containing the summary report data.
    """
    logger.info(f"Generating daily summary report for date: {report_date.isoformat()}")

    # Define start and end of the report_date for datetime filtering
    start_datetime = datetime.combine(report_date, time.min)
    end_datetime = datetime.combine(report_date, time.max)

    # Total feedback for the day
    total_feedback_today = (
        db.query(func.count(FeedbackModel.id))
        .filter(
            FeedbackModel.created_at >= start_datetime,
            FeedbackModel.created_at <= end_datetime
        )
        .scalar() or 0 # Ensure 0 if scalar() returns None
    )

    # Sentiment breakdown for the day
    sentiment_query = (
        db.query(
            FeedbackModel.sentiment_label,
            func.count(FeedbackModel.id).label("count")
        )
        .filter(
            FeedbackModel.created_at >= start_datetime,
            FeedbackModel.created_at <= end_datetime
        )
        .filter(FeedbackModel.sentiment_label.isnot(None))
        .filter(FeedbackModel.sentiment_label != "") # Explicitly filter out empty strings
        .group_by(FeedbackModel.sentiment_label)
        .all()
    )

    sentiment_breakdown_today = {"positive": 0, "negative": 0, "neutral": 0}
    for row in sentiment_query:
        if row.sentiment_label in sentiment_breakdown_today: # Check if label is one we track
            sentiment_breakdown_today[row.sentiment_label] = row.count

    # Highly negative feedback for the day (e.g., rating 1 or 2)
    # Ensure the 'rating' column exists and is appropriate for this logic
    highly_negative_today = 0
    if hasattr(FeedbackModel, 'rating'): # Check if FeedbackModel has 'rating' attribute
        highly_negative_today = (
            db.query(func.count(FeedbackModel.id))
            .filter(
                FeedbackModel.created_at >= start_datetime,
                FeedbackModel.created_at <= end_datetime
            )
            .filter(FeedbackModel.rating.in_([1, 2])) # Assuming 1 and 2 are 'highly negative'
            .scalar() or 0
        )

    report_data = {
        "report_date": report_date.isoformat(),
        "total_feedback_today": total_feedback_today,
        "sentiment_breakdown_today": sentiment_breakdown_today,
        "highly_negative_today": highly_negative_today
    }

    logger.info(f"Report data for {report_date.isoformat()}: {report_data}")
    return report_data

# Example usage (for direct testing of this service)
# if __name__ == '__main__':
#     from cx360.backend.database import SessionLocal, engine, Base
#     # Create tables if they don't exist (for local testing)
#     # Base.metadata.create_all(bind=engine)

#     test_db_session = SessionLocal()
#     try:
#         # Optional: Add some mock data to test_db_session for the report_date
#         # report_for_date = date(2023, 10, 26) # Example date
#         report_for_date = date.today() # Report for today

#         # Example: Add a positive feedback for today
#         # test_db_session.add(FeedbackModel(
#         #     feedback_text="Great service today!", rating=5, sentiment_label="positive", sentiment_score=0.9,
#         #     created_at=datetime.now()
#         # ))
#         # test_db_session.add(FeedbackModel(
#         #     feedback_text="Bad service today!", rating=1, sentiment_label="negative", sentiment_score=-0.8,
#         #     created_at=datetime.now()
#         # ))
#         # test_db_session.commit()

#         summary = generate_daily_summary_report(test_db_session, report_date=report_for_date)
#         print("Generated Report:", summary)
#     except Exception as e:
#         print(f"Error during example usage: {e}")
#     finally:
#         test_db_session.close()
```
