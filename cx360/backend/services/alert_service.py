import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from cx360.backend.models.feedback import Feedback as FeedbackModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Alerting Constants ---
NEGATIVE_FEEDBACK_THRESHOLD: int = 3 # Number of negative feedback items to trigger an alert
ALERT_TIME_WINDOW_HOURS: int = 1   # Time window in hours to check for negative feedback

def check_for_recent_negative_feedback_alert(db: Session) -> str | None:
    """
    Checks for a surge in negative feedback within a defined time window.
    If the count of 'negative' feedback entries meets or exceeds NEGATIVE_FEEDBACK_THRESHOLD
    within the last ALERT_TIME_WINDOW_HOURS, an alert message is returned.

    Args:
        db: The SQLAlchemy database session.

    Returns:
        An alert message string if the threshold is met, otherwise None.
    """
    try:
        # Calculate the start of the time window
        time_window_start = datetime.utcnow() - timedelta(hours=ALERT_TIME_WINDOW_HOURS)

        # Query for negative feedback within the time window
        negative_feedback_count = (
            db.query(func.count(FeedbackModel.id))
            .filter(
                FeedbackModel.sentiment_label == "negative",
                FeedbackModel.created_at >= time_window_start
            )
            .scalar()
        )

        if negative_feedback_count is None: # Should not happen with func.count, but good practice
            negative_feedback_count = 0

        logger.info(
            f"Checked for negative feedback alert: Found {negative_feedback_count} negative feedback entries "
            f"in the last {ALERT_TIME_WINDOW_HOURS} hour(s)."
        )

        if negative_feedback_count >= NEGATIVE_FEEDBACK_THRESHOLD:
            alert_message = (
                f"ALERT: High volume of negative feedback detected! "
                f"{negative_feedback_count} negative entries in the last {ALERT_TIME_WINDOW_HOURS} hour(s)."
            )
            logger.warning(alert_message) # Log the alert as a warning
            return alert_message

        return None # No alert condition met

    except Exception as e:
        logger.error(f"Error during negative feedback alert check: {e}", exc_info=True)
        return None # Return None on error to prevent disrupting other operations


# Example usage (for testing this service directly, not part of the main app flow usually)
# if __name__ == '__main__':
#     # This requires a database session and engine setup, similar to conftest.py or main.py
#     # from cx360.backend.database import SessionLocal, engine, Base
#     # Base.metadata.create_all(bind=engine) # Ensure tables exist if using a real test DB
#     # test_db = SessionLocal()
#     try:
#         # --- Setup mock data for testing ---
#         # 1. Create some recent negative feedback
#         # for i in range(NEGATIVE_FEEDBACK_THRESHOLD):
#         #     fb = FeedbackModel(
#         #         feedback_text=f"This is terrible service {i+1}",
#         #         sentiment_label="negative",
#         #         sentiment_score=-0.8,
#         #         created_at=datetime.utcnow() - timedelta(minutes=30) # Within the last hour
#         #     )
#         #     test_db.add(fb)
#         # test_db.commit()
+
#         # 2. Call the alert check function
#         # alert = check_for_recent_negative_feedback_alert(test_db)
#         # if alert:
#         #     print(f"Alert Triggered: {alert}")
#         # else:
#         #     print("No alert condition met.")
+
#         # --- Clean up mock data ---
#         # test_db.query(FeedbackModel).delete()
#         # test_db.commit()
#         pass # Placeholder for actual test setup if running standalone
#     finally:
#         # test_db.close()
#         pass
```
