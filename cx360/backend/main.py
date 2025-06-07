from fastapi import FastAPI

# Import database engine, Base, and models to ensure tables are created
from cx360.backend.database import engine, Base
# Import your SQLAlchemy models here so Base knows about them
import cx360.backend.models.user # This import is crucial
import cx360.backend.models.feedback # This import is crucial for Feedback table creation

# Import routers
from cx360.backend.routes import auth as auth_router
from cx360.backend.routes import feedback as feedback_router
from cx360.backend.routes import dashboard as dashboard_router # Added dashboard router import
# If you have other routers, import them here
# from .routes import other_module as other_router

# --- Email Configuration ---
from fastapi_mail import ConnectionConfig, FastMail
from pydantic import EmailStr # EmailStr is already used in models, but good to ensure it's available here
import os

# FastMail Configuration
# Using SUPPRESS_SEND=1 for "console backend" behavior.
# Actual emails will not be sent; intent will be logged by the email service.
# Environment variables for actual SMTP server are placeholders if SUPPRESS_SEND=1.
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "consoleuser"), # Placeholder for console
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "consolepass"), # Placeholder for console
    MAIL_FROM=EmailStr(os.getenv("MAIL_FROM", "cx360-alerts@example.com")),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")), # Placeholder
    MAIL_SERVER=os.getenv("MAIL_SERVER", "localhost"),     # Placeholder
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "False").lower() == "true", # Default to False for console/dummy
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",  # Default to False for console/dummy
    USE_CREDENTIALS=os.getenv("MAIL_USE_CREDENTIALS", "False").lower() == "true", # Default to False for console
    VALIDATE_CERTS=os.getenv("MAIL_VALIDATE_CERTS", "False").lower() == "true", # Default to False for console
    SUPPRESS_SEND=int(os.getenv("MAIL_SUPPRESS_SEND", "1")) # 1 to suppress, 0 to send
)
fm = FastMail(conf)
# --- End Email Configuration ---

# Create all tables in the database.
# This is suitable for development. For production, you'd typically use migrations (e.g., Alembic).
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully (if they didn't exist).")
except Exception as e:
    print(f"Error creating database tables: {e}")
    # Depending on the app, you might want to exit or handle this differently
    # For now, we'll let it continue, but in production, this could be a critical failure.

app = FastAPI(
    title="CX360 API",
    description="API for Customer Experience 360 Platform",
    version="0.1.0",
)

# --- Scheduler Setup ---
import logging # Ensure logging is configured for scheduler messages
from cx360.backend.scheduler import init_scheduler, shutdown_scheduler

# Configure basic logging if not already set up elsewhere (e.g., for Uvicorn's logger)
# This helps see scheduler logs. APScheduler also uses the 'apscheduler' logger.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Logger for main.py

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup: Initializing scheduler...")
    init_scheduler()
    # Any other startup tasks can go here

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown: Shutting down scheduler...")
    shutdown_scheduler()
    # Any other shutdown tasks can go here
# --- End Scheduler Setup ---

# Include routers
app.include_router(auth_router.router)
app.include_router(feedback_router.router)
app.include_router(dashboard_router.router) # Added dashboard router
# app.include_router(other_router.router, prefix="/other", tags=["Other Module"])


@app.get("/")
async def root():
    return {"message": "Welcome to CX360 API"}

# Optional: Add startup/shutdown events if needed
# @app.on_event("startup")
# async def startup_event():
#     # Things to do on startup, e.g., connect to other services
#     pass

# @app.on_event("shutdown")
# async def shutdown_event():
#     # Things to do on shutdown
#     pass

# To run this app (assuming uvicorn is installed):
# uvicorn cx360.backend.main:app --reload --host 0.0.0.0 --port 8000
# Ensure PYTHONPATH includes the root of your project or run from the directory containing cx360
# Example: PYTHONPATH=$PYTHONPATH:/path/to/your/project uvicorn cx360.backend.main:app --reload
# Or, if in the 'backend' directory: cd .. && uvicorn cx360.backend.main:app --reload
# Or, if your IDE handles it, or you use a project runner like Poetry/PDM.
