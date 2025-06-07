import pytest
from fastapi.testclient import TestClient
# from unittest.mock import MagicMock # pytest-mock provides 'mocker' fixture

# The 'client' fixture is automatically available from conftest.py
# The 'mocker' fixture is from pytest-mock (installed in requirements)

# Assuming User model and UserResponse schema are defined
from cx360.backend.models.user import User as DBUser # SQLAlchemy model
from cx360.backend.models.user import UserResponse, UserRole # Pydantic schema

# Test User Registration (/auth/register)
def test_register_user_success(client: TestClient, mocker):
    # Mock database helper functions used by the /register route
    mocker.patch("cx360.backend.routes.auth.get_user_by_email", return_value=None)
    mocker.patch("cx360.backend.routes.auth.get_user_by_username", return_value=None)

    # Mock create_db_user to return a dummy created user (as UserResponse)
    # This should align with what create_db_user actually returns or what UserResponse expects
    mock_created_user = UserResponse(
        id=1,
        username="testuser",
        email="test@example.com",
        role=UserRole.agent,
        is_active=True,
        created_at="2023-01-01T12:00:00Z" # Example datetime string
    )
    mocker.patch("cx360.backend.routes.auth.create_db_user", return_value=mock_created_user)

    response = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123", "role": "agent"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data # Ensure password is not returned

def test_register_user_email_exists(client: TestClient, mocker):
    # Mock get_user_by_email to simulate finding an existing user
    mocker.patch("cx360.backend.routes.auth.get_user_by_email", return_value=DBUser(id=1, email="existing@example.com", username="otheruser"))
    # get_user_by_username might also be called, ensure it doesn't conflict or mock it too
    mocker.patch("cx360.backend.routes.auth.get_user_by_username", return_value=None)


    response = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "existing@example.com", "password": "password123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_register_user_username_exists(client: TestClient, mocker):
    mocker.patch("cx360.backend.routes.auth.get_user_by_email", return_value=None)
    mocker.patch("cx360.backend.routes.auth.get_user_by_username", return_value=DBUser(id=1, email="test@example.com", username="existinguser"))

    response = client.post(
        "/auth/register",
        json={"username": "existinguser", "email": "newemail@example.com", "password": "password123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"


# Test User Login (/auth/token)
def test_login_success(client: TestClient, mocker):
    # Mock user retrieval and password verification
    # This DBUser needs to have a 'hashed_password' attribute
    mock_user_from_db = DBUser(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="some_hashed_password", # Actual hash doesn't matter due to verify_password mock
        role=UserRole.agent, # Ensure role is an enum member if UserRole is an Enum
        is_active=True
    )
    mocker.patch("cx360.backend.routes.auth.get_user_by_username", return_value=mock_user_from_db)
    mocker.patch("cx360.backend.services.auth_service.verify_password", return_value=True) # Patch in auth_service

    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "password123"}, # Form data for token endpoint
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_not_found(client: TestClient, mocker):
    mocker.patch("cx360.backend.routes.auth.get_user_by_username", return_value=None)

    response = client.post(
        "/auth/token",
        data={"username": "nonexistentuser", "password": "password123"},
    )
    assert response.status_code == 401 # Or 400/404 depending on specific HTTPException in route
    # The example route raises 401 for incorrect username or password
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_incorrect_password(client: TestClient, mocker):
    mock_user_from_db = DBUser(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="some_hashed_password",
        role=UserRole.agent,
        is_active=True
    )
    mocker.patch("cx360.backend.routes.auth.get_user_by_username", return_value=mock_user_from_db)
    mocker.patch("cx360.backend.services.auth_service.verify_password", return_value=False) # Password verification fails

    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

# Test Get Current User (/auth/users/me) - Requires a valid token
def test_get_current_user_me_success(client: TestClient, mocker):
    # 1. Mock get_user_by_username that will be called by get_current_user
    mock_db_user = DBUser(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        role=UserRole.agent,
        is_active=True,
        created_at="2023-01-01T00:00:00" # Needs to be a valid datetime or string for UserResponse
    )
    mocker.patch("cx360.backend.routes.auth.get_user_by_username", return_value=mock_db_user)

    # 2. Create a valid token for "testuser"
    # We need auth_service.create_access_token for this.
    # Ensure constants (SECRET_KEY, ALGORITHM) are consistent with those used by the app for token decoding.
    # Pytest.ini should set these for the test environment.
    # The override_auth_service_constants fixture in test_auth_service.py won't apply here directly
    # unless we also apply it globally or replicate its logic for token generation.
    # For simplicity, let's assume auth_service uses env vars set by pytest.ini
    from cx360.backend.services.auth_service import create_access_token

    # Use the actual SECRET_KEY and ALGORITHM that auth_service is configured with for this test run
    # (these should come from environment variables set by pytest.ini)
    token_data = {"sub": "testuser", "scopes": [UserRole.agent.value]} # Match token payload structure
    access_token = create_access_token(data=token_data)

    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/auth/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["role"] == UserRole.agent.value # Ensure enum value is checked

def test_get_current_user_me_invalid_token(client: TestClient):
    headers = {"Authorization": "Bearer aninvalidtoken"}
    response = client.get("/auth/users/me", headers=headers)
    assert response.status_code == 401 # Expect 401 for invalid token
    assert "Could not validate credentials" in response.json()["detail"]

def test_get_current_user_me_inactive_user(client: TestClient, mocker):
    mock_db_user_inactive = DBUser(
        id=2, username="inactiveuser", email="inactive@example.com",
        hashed_password="hashed_password", role=UserRole.agent, is_active=False,
        created_at="2023-01-01T00:00:00"
    )
    mocker.patch("cx360.backend.routes.auth.get_user_by_username", return_value=mock_db_user_inactive)

    from cx360.backend.services.auth_service import create_access_token
    token_data = {"sub": "inactiveuser", "scopes": [UserRole.agent.value]}
    access_token = create_access_token(data=token_data)

    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/auth/users/me", headers=headers)

    assert response.status_code == 400 # From get_current_active_user
    assert response.json()["detail"] == "Inactive user"

# Note: For the /users/me tests, the token generation (create_access_token)
# uses the auth_service directly. This service's JWT constants (SECRET_KEY, ALGORITHM)
# should be loaded from environment variables set by pytest.ini for consistency.
# If auth_service.py has hardcoded constants, those tests might fail or behave unexpectedly
# unless monkeypatched here as well, similar to test_auth_service.py.
# The conftest.py doesn't globally monkeypatch auth_service constants.
# For robust testing, ensure auth_service.py loads its config from env vars.
# The test_auth_service.py uses a fixture to monkeypatch these, which is good for that module.
# Here, we rely on pytest.ini's env vars being picked up by auth_service.py.
```
