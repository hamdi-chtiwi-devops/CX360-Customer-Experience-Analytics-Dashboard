import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool # Recommended for SQLite in tests

# Import your FastAPI app and SQLAlchemy Base
from cx360.backend.main import app # Adjusted: main app for TestClient
from cx360.backend.database import Base, get_db # Base for creating tables, get_db for overriding

# --- Test Database Setup ---
# Using an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:" # In-memory SQLite

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, # Needed for SQLite in-memory
    poolclass=StaticPool, # Use StaticPool for SQLite in tests
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Fixture to Override get_db Dependency ---
@pytest.fixture(scope="function") # function scope: DB is created/destroyed for each test
def db_session():
    # Create all tables for each test function
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after each test function
        Base.metadata.drop_all(bind=engine)

# --- Fixture for TestClient ---
@pytest.fixture(scope="function")
def client(db_session): # Depends on db_session to ensure tables are set up

    # Override the get_db dependency in the app
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close() # Session is managed by db_session fixture

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up overrides after tests if necessary, though TestClient context manager might handle it
    app.dependency_overrides.clear()


# --- Optional: Fixture for authenticated client ---
# This would require a way to create a user and log them in to get a token.
# For now, tests can handle token generation manually if needed for protected routes.

# Example (more advanced, if you want an auto-authenticated client):
# @pytest.fixture(scope="function")
# def authenticated_client(client, db_session):
#     from cx360.backend.services.auth_service import create_access_token
#     from cx360.backend.models.user import UserCreate # Pydantic model
#     from cx360.backend.routes.auth import create_db_user # Helper from auth routes

#     # Create a test user directly in the test DB
#     test_user_data = UserCreate(username="testclientuser", email="testclient@example.com", password="testpassword")
#     user = create_db_user(db=db_session, user=test_user_data)

#     # Generate a token for this user
#     token_data = {"sub": user.username, "scopes": [user.role.value]}
#     token = create_access_token(data=token_data)

#     client.headers.update({"Authorization": f"Bearer {token}"})
#     yield client
#     client.headers.clear() # Clean up headers

# Note: The above authenticated_client fixture assumes create_db_user and UserCreate
# are accessible and work as expected. It also directly uses auth_service.create_access_token.
# The SECRET_KEY for create_access_token would ideally be the one set in pytest.ini for consistency.
# This might require auth_service to pick up env vars for its constants, or monkeypatching here too.
# For now, keeping it simple: route tests will mock DB interactions as per the plan.
# If routes are tested against a real (test) DB, this fixture becomes more relevant.

# Pytest will automatically discover fixtures in conftest.py files.
# No need to import them explicitly in test files in the same directory or subdirectories.
