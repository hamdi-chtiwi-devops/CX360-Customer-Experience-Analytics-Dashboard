from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import date, time, datetime, timedelta # Ensure datetime and timedelta are imported
import logging
import pytz # For timezone awareness

# Assuming SessionLocal is correctly defined in database.py to create DB sessions
from cx360.backend.database import SessionLocal
from cx360.backend.services.report_service import generate_daily_summary_report

logger = logging.getLogger(__name__)
if not logger.handlers: # Ensure logger is configured
    logging.basicConfig(level=logging.INFO)

# Initialize scheduler with UTC timezone for consistency
scheduler = AsyncIOScheduler(timezone=pytz.utc)

async def scheduled_daily_report_job():
    """
    The actual job executed by the scheduler.
    It creates a new DB session, generates the daily report, and logs it.
    """
    logger.info(f"Executing scheduled daily report job at {datetime.now(pytz.utc).isoformat()} UTC...")
    db = None
    try:
        db = SessionLocal()
        # Generate report for "yesterday" because this job runs early in the morning (e.g., 1 AM UTC).
        # This ensures all data for the previous day is captured.
        report_date_to_generate = date.today() - timedelta(days=1)

        report_data = generate_daily_summary_report(db, report_date=report_date_to_generate)
        # The report_service already logs the generated data.
        # Here, we just confirm the job execution and for which date the report was made.
        logger.info(f"Daily summary report job completed for date: {report_date_to_generate.isoformat()}.")

    except Exception as e:
        logger.error(f"Error during scheduled daily report job: {e}", exc_info=True)
    finally:
        if db:
            db.close()
            logger.info("Database session closed for scheduled job.")

def init_scheduler():
    """
    Initializes and starts the scheduler, adding the daily report job.
    """
    if scheduler.running:
        logger.info("Scheduler is already running.")
        return

    # Add job to run daily. Example: At 01:00 AM UTC.
    # CronTrigger fields: year, month, day, week, day_of_week, hour, minute, second, timezone
    # Note: APScheduler uses local time of the scheduler by default unless timezone is specified
    # in AsyncIOScheduler constructor or on the trigger. We set UTC on scheduler.
    try:
        scheduler.add_job(
            scheduled_daily_report_job,
            trigger=CronTrigger(hour=1, minute=0, timezone="UTC"), # Runs daily at 1:00 AM UTC
            id="daily_summary_report_job",  # Unique ID for the job
            name="Daily Feedback Summary Report",
            replace_existing=True, # Replace job if one with the same ID already exists
            misfire_grace_time=300 # Grace time for misfires (e.g. 5 minutes)
        )
        logger.info("Daily summary report job scheduled to run at 01:00 UTC.")
    except Exception as e:
        logger.error(f"Error adding job to scheduler: {e}", exc_info=True)
        return # Do not start scheduler if job scheduling fails

    try:
        scheduler.start()
        logger.info("Scheduler started successfully.")
    except Exception as e:
        logger.error(f"Error starting the scheduler: {e}", exc_info=True)

# To be called from main.py on application shutdown
def shutdown_scheduler():
    if scheduler.running:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown(wait=False) # wait=False to not block shutdown
        logger.info("Scheduler shut down.")

# Example of how to run this for testing (not part of FastAPI app flow):
# if __name__ == "__main__":
#     import asyncio
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     init_scheduler()
#     try:
#         asyncio.get_event_loop().run_forever()
#     except (KeyboardInterrupt, SystemExit):
#         shutdown_scheduler()

# No longer need separate timedelta import
```
