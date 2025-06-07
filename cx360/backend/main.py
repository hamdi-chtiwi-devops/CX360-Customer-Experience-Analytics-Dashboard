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
