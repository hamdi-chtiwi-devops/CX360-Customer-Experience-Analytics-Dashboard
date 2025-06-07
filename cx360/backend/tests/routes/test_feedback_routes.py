import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session # For type hinting if needed for mocks
from datetime import datetime, timezone

# Fixtures 'client' and 'db_session' are from conftest.py
# Mocker fixture is from pytest-mock

from cx360.backend.models.feedback import FeedbackResponse, FeedbackCreate, FeedbackUpdate
from cx360.backend.models.user import User as DBUser, UserRole, UserResponse as PydanticUserResponse
from cx360.backend.services.auth_service import create_access_token

# Helper function to create a token for a test user
# This avoids direct DB interaction in this test file for user creation,
# assuming user data for token is what matters.
def get_auth_headers(username="testuser", role=UserRole.agent, user_id=1):
    # The "sub" in the token is typically username or email.
    # The "scopes" or other claims like "role" might be used by your dependencies.
    # Ensure this matches what your get_current_active_user expects from the token payload.
    # In auth.py, get_current_user decodes token and gets username from "sub".
    # Then it fetches user by username.
    token_data = {"sub": username, "scopes": [role.value], "user_id": user_id} # Added user_id for clarity if needed

    # Use the SECRET_KEY and ALGORITHM that auth_service is configured with (from pytest.ini env vars)
    access_token = create_access_token(data=token_data)
    return {"Authorization": f"Bearer {access_token}"}

# --- Test Create Feedback Endpoint (POST /feedback/) ---

def test_create_feedback_authenticated_user(client: TestClient, mocker):
    headers = get_auth_headers(username="authuser", user_id=123)

    # Mock get_current_active_user to return a dummy user based on token
    # This bypasses DB lookup for user in get_current_active_user
    mock_current_user = DBUser(id=123, username="authuser", email="auth@example.com", role=UserRole.agent, is_active=True)
    mocker.patch("cx360.backend.routes.feedback.get_current_active_user", return_value=mock_current_user)

    # Mock the database creation function
    # It should return a Feedback object that can be serialized into FeedbackResponse
    mock_created_feedback_db = object() # Placeholder for a MagicMock or a real-like object
    mock_created_feedback_db.id = 1
    mock_created_feedback_db.customer_name = "Test Customer"
    mock_created_feedback_db.email = "customer@example.com"
    mock_created_feedback_db.rating = 5
    mock_created_feedback_db.feedback_text = "Great service!"
    mock_created_feedback_db.source = "website"
    mock_created_feedback_db.user_id = 123 # Should match the authenticated user's ID
    mock_created_feedback_db.created_at = datetime.now(timezone.utc)
    mock_created_feedback_db.updated_at = datetime.now(timezone.utc)

    mocker.patch("cx360.backend.routes.feedback.db_create_feedback", return_value=mock_created_feedback_db)

    feedback_data = {
        "customer_name": "Test Customer",
        "email": "customer@example.com",
        "rating": 5,
        "feedback_text": "Great service!",
        "source": "website"
        # user_id is not sent in payload; it's derived from current_user in the route
    }
    response = client.post("/feedback/", json=feedback_data, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["feedback_text"] == feedback_data["feedback_text"]
    assert data["rating"] == feedback_data["rating"]
    assert data["user_id"] == 123 # Check if user_id is correctly associated
    assert "id" in data

def test_create_feedback_anonymous_user_allowed(client: TestClient, mocker):
    # Route allows anonymous if get_current_active_user dependency is made optional
    # The current feedback route POST / has Optional[UserModel] = Depends(get_current_active_user)
    # So, if no token is provided, current_user will be None.

    mock_created_feedback_db = object()
    mock_created_feedback_db.id = 2
    mock_created_feedback_db.customer_name = "Anon Customer"
    mock_created_feedback_db.email = "anon@example.com"
    mock_created_feedback_db.rating = 4
    mock_created_feedback_db.feedback_text = "Good!"
    mock_created_feedback_db.source = "app"
    mock_created_feedback_db.user_id = None # Expect user_id to be None
    mock_created_feedback_db.created_at = datetime.now(timezone.utc)
    mock_created_feedback_db.updated_at = datetime.now(timezone.utc)

    mocker.patch("cx360.backend.routes.feedback.db_create_feedback", return_value=mock_created_feedback_db)
    # Mock get_current_active_user to simulate no user (it won't be called if no token)
    # Or, ensure the dependency correctly handles optional authentication

    feedback_data = {
        "customer_name": "Anon Customer",
        "email": "anon@example.com",
        "rating": 4,
        "feedback_text": "Good!",
        "source": "app"
    }
    # No headers for anonymous request
    response = client.post("/feedback/", json=feedback_data)

    assert response.status_code == 201
    data = response.json()
    assert data["feedback_text"] == feedback_data["feedback_text"]
    assert data["user_id"] is None

def test_create_feedback_invalid_data(client: TestClient):
    headers = get_auth_headers() # Needs auth if endpoint is protected generally
    # Missing feedback_text (which is required in Pydantic model FeedbackCreate)
    feedback_data = {"rating": 3}
    response = client.post("/feedback/", json=feedback_data, headers=headers)
    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation error

# --- Test Read Feedback Endpoints ---

def test_read_one_feedback_exists(client: TestClient, mocker):
    mock_feedback_db = object()
    mock_feedback_db.id = 100
    mock_feedback_db.feedback_text = "Found me!"
    mock_feedback_db.rating = 5
    mock_feedback_db.customer_name = "Cust"
    mock_feedback_db.email = "cust@mail.com"
    mock_feedback_db.source = "web"
    mock_feedback_db.user_id = None
    mock_feedback_db.created_at = datetime.now(timezone.utc)
    mock_feedback_db.updated_at = datetime.now(timezone.utc)

    mocker.patch("cx360.backend.routes.feedback.db_get_feedback", return_value=mock_feedback_db)

    response = client.get("/feedback/100")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 100
    assert data["feedback_text"] == "Found me!"

def test_read_one_feedback_not_found(client: TestClient, mocker):
    mocker.patch("cx360.backend.routes.feedback.db_get_feedback", return_value=None)
    response = client.get("/feedback/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Feedback not found"

def test_read_all_feedback_multiple_exist(client: TestClient, mocker):
    mock_fb1 = FeedbackResponse(id=1, feedback_text="FB1", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc), rating=3)
    mock_fb2 = FeedbackResponse(id=2, feedback_text="FB2", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc), rating=4)

    mocker.patch("cx360.backend.routes.feedback.db_get_all_feedback", return_value=[mock_fb1, mock_fb2])

    response = client.get("/feedback/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["feedback_text"] == "FB1"
    assert data[1]["feedback_text"] == "FB2"

def test_read_all_feedback_empty(client: TestClient, mocker):
    mocker.patch("cx360.backend.routes.feedback.db_get_all_feedback", return_value=[])
    response = client.get("/feedback/")
    assert response.status_code == 200
    assert response.json() == []

# --- Test Update Feedback Endpoint (PUT /feedback/{feedback_id}) ---
# This endpoint requires authentication by default in routes/feedback.py
# `current_user: UserModel = Depends(get_current_active_user)`

def test_update_feedback_success_owner(client: TestClient, mocker):
    user_id_owner = 777
    feedback_id_to_update = 1
    headers = get_auth_headers(username="owneruser", user_id=user_id_owner)

    # Mock get_current_active_user to return the owner
    mock_owner_user = DBUser(id=user_id_owner, username="owneruser", role=UserRole.agent, is_active=True)
    mocker.patch("cx360.backend.routes.feedback.get_current_active_user", return_value=mock_owner_user)

    # Mock db_update_feedback to return the updated feedback object
    # This mock simulates that the feedback was found and the user was authorized
    updated_feedback_response = FeedbackResponse(
        id=feedback_id_to_update,
        feedback_text="Updated text",
        rating=4,
        customer_name="Original Owner", # These fields would be from the original record
        user_id=user_id_owner, # User ID remains the same
        created_at=datetime.now(timezone.utc), # Original creation time
        updated_at=datetime.now(timezone.utc)  # New update time
    )
    mocker.patch("cx360.backend.routes.feedback.db_update_feedback", return_value=updated_feedback_response)

    update_data = {"feedback_text": "Updated text", "rating": 4}
    response = client.put(f"/feedback/{feedback_id_to_update}", json=update_data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["feedback_text"] == "Updated text"
    assert data["rating"] == 4
    assert data["id"] == feedback_id_to_update
    assert data["user_id"] == user_id_owner


def test_update_feedback_not_found(client: TestClient, mocker):
    headers = get_auth_headers()
    mock_current_user = DBUser(id=1, username="anyuser", role=UserRole.agent, is_active=True)
    mocker.patch("cx360.backend.routes.feedback.get_current_active_user", return_value=mock_current_user)

    # Mock db_update_feedback to simulate feedback not found (or not authorized, route returns 404 then)
    mocker.patch("cx360.backend.routes.feedback.db_update_feedback", return_value=None)

    update_data = {"feedback_text": "Doesn't matter"}
    response = client.put("/feedback/9999", json=update_data, headers=headers)
    assert response.status_code == 404
    assert "Feedback not found or not authorized to update" in response.json()["detail"]


def test_update_feedback_not_owner_forbidden(client: TestClient, mocker):
    owner_id = 10
    attacker_id = 20
    feedback_id = 30

    # Simulate attacker trying to update feedback owned by owner_id
    attacker_headers = get_auth_headers(username="attacker", user_id=attacker_id)
    mock_attacker_user = DBUser(id=attacker_id, username="attacker", role=UserRole.agent, is_active=True)
    mocker.patch("cx360.backend.routes.feedback.get_current_active_user", return_value=mock_attacker_user)

    # Mock the db_update_feedback to raise the HTTPException for authorization
    # This means the authorization logic is within db_update_feedback helper
    from fastapi import HTTPException
    mocker.patch("cx360.backend.routes.feedback.db_update_feedback",
                 side_effect=HTTPException(status_code=403, detail="Not authorized to update this feedback"))

    update_data = {"feedback_text": "Malicious update"}
    response = client.put(f"/feedback/{feedback_id}", json=update_data, headers=attacker_headers)

    # The route itself will catch the HTTPException from the service and re-raise, or return its own.
    # If db_update_feedback returns None because of auth, then route returns 404.
    # If db_update_feedback raises 403, then route re-raises 403.
    # Current db_update_feedback in feedback.py raises 403.
    assert response.status_code == 403
    assert "Not authorized to update this feedback" in response.json()["detail"]


# --- Test Delete Feedback Endpoint (DELETE /feedback/{feedback_id}) ---
# Similar authentication and authorization logic as update

def test_delete_feedback_success_owner(client: TestClient, mocker):
    user_id_owner = 888
    feedback_id_to_delete = 2
    headers = get_auth_headers(username="ownerdeleter", user_id=user_id_owner)

    mock_owner_user = DBUser(id=user_id_owner, username="ownerdeleter", role=UserRole.agent, is_active=True)
    mocker.patch("cx360.backend.routes.feedback.get_current_active_user", return_value=mock_owner_user)

    # Mock db_delete_feedback to simulate successful deletion
    # It might return the deleted object or True
    mock_deleted_feedback_obj = FeedbackResponse(id=feedback_id_to_delete, feedback_text="deleted", created_at=datetime.now(), updated_at=datetime.now())
    mocker.patch("cx360.backend.routes.feedback.db_delete_feedback", return_value=mock_deleted_feedback_obj)

    response = client.delete(f"/feedback/{feedback_id_to_delete}", headers=headers)
    assert response.status_code == 204 # No content on successful deletion

def test_delete_feedback_not_found(client: TestClient, mocker):
    headers = get_auth_headers()
    mock_current_user = DBUser(id=1, username="anydeleter", role=UserRole.agent, is_active=True)
    mocker.patch("cx360.backend.routes.feedback.get_current_active_user", return_value=mock_current_user)

    mocker.patch("cx360.backend.routes.feedback.db_delete_feedback", return_value=None) # Simulate not found or not authorized

    response = client.delete("/feedback/9998", headers=headers)
    assert response.status_code == 404
    assert "Feedback not found or not authorized to delete" in response.json()["detail"]


def test_delete_feedback_not_owner_forbidden(client: TestClient, mocker):
    feedback_id_to_delete = 40
    # Setup: Attacker user
    attacker_headers = get_auth_headers(username="attacker_deleter", user_id=200)
    mock_attacker_user = DBUser(id=200, username="attacker_deleter", role=UserRole.agent, is_active=True)
    mocker.patch("cx360.backend.routes.feedback.get_current_active_user", return_value=mock_attacker_user)

    # Mock db_delete_feedback to raise 403 if authorization fails inside it
    from fastapi import HTTPException
    mocker.patch("cx360.backend.routes.feedback.db_delete_feedback",
                 side_effect=HTTPException(status_code=403, detail="Not authorized to delete this feedback"))

    response = client.delete(f"/feedback/{feedback_id_to_delete}", headers=attacker_headers)
    assert response.status_code == 403
    assert "Not authorized to delete this feedback" in response.json()["detail"]

# Note: Admin role tests (e.g. admin can delete/update any feedback) are not included here
# but would follow a similar pattern: create an admin user, get their token,
# and mock the db_update/delete_feedback functions to *not* raise auth error for admin.
# Or, if auth logic is in the route, mock get_current_active_user to return an admin.
```
