from sqlalchemy.orm import Session
from typing import List
import logging

# Import the alert checking function
from cx360.backend.services.alert_service import check_for_recent_negative_feedback_alert

logger = logging.getLogger(__name__)
if not logger.handlers: # Ensure logger is configured
    logging.basicConfig(level=logging.INFO)

def generate_recommendations(db: Session) -> List[str]:
    """
    Generates a list of actionable recommendations based on current data and alerts.
    """
    recommendations: List[str] = []

    # 1. Recommendation based on negative feedback alert
    try:
        alert_message = check_for_recent_negative_feedback_alert(db)
        if alert_message:
            # Make the recommendation more actionable than just the alert message
            recommendations.append(
                "Action: Investigate the recent surge in negative feedback. "
                "Review comments and identify common themes or urgent issues."
            )
        else:
            # Optional: Add a positive note if no alert
            # recommendations.append("Good work: No high volume of negative feedback detected recently.")
            pass # Or simply don't add a recommendation if no alert

    except Exception as e:
        logger.error(f"Error generating recommendation from alert service: {e}", exc_info=True)
        recommendations.append(
            "Notice: Could not check negative feedback alert status for recommendations due to an error."
        )

    # 2. Static/Mocked Recommendation: Encourage reviewing positive feedback for insights
    recommendations.append(
        "Tip: Regularly review positive feedback to identify strengths and best practices. "
        "Share positive comments with your team to boost morale."
    )

    # 3. Static/Mocked Recommendation: Suggest checking feedback trends
    recommendations.append(
        "Suggestion: Monitor feedback trends over time using the dashboard charts. "
        "Look for patterns in ratings and sentiment to guide improvements."
    )

    # Limit to 2-3 recommendations as requested
    # If the alert recommendation is present, we might have 3. If not, 2.
    # This logic is okay as is, or could be more sophisticated to always return a fixed number.

    logger.info(f"Generated {len(recommendations)} recommendations.")
    return recommendations

# Example usage (for direct testing)
# if __name__ == '__main__':
#     from cx360.backend.database import SessionLocal
#     test_db = SessionLocal()
#     try:
#         recs = generate_recommendations(test_db)
#         print("\nGenerated Recommendations:")
#         for i, rec in enumerate(recs):
#             print(f"{i+1}. {rec}")
#     finally:
#         test_db.close()
```
