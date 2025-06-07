import pytest
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
import time

from cx360.backend.services import auth_service

# These constants will be used by tests, overriding what's in auth_service
# The override can be done via monkeypatch in a fixture or by direct assignment if auth_service allows it.
# Pytest.ini sets environment variables, which auth_service.py should ideally load.
# Let's assume auth_service.py loads these from os.getenv with defaults.
# If auth_service.py defines them as global constants directly, monkeypatching is the way.

# For this test, we'll rely on pytest.ini to set env vars, and assume auth_service.py uses them.
# If not, the monkeypatch fixture below is the alternative.
# Reading from auth_service to confirm how they are defined:
# SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key") -> This would work with pytest.ini
# If it's SECRET_KEY = "your-default-secret-key", then monkeypatch is needed.
# The example provided uses global constants in auth_service.py, so monkeypatch is appropriate.

TEST_SECRET_KEY = auth_service.SECRET_KEY # Use the one from pytest.ini via auth_service
TEST_ALGORITHM = auth_service.ALGORITHM
TEST_ACCESS_TOKEN_EXPIRE_MINUTES = auth_service.ACCESS_TOKEN_EXPIRE_MINUTES

# This fixture will run for all tests in this module
@pytest.fixture(autouse=True)
def override_auth_service_constants(monkeypatch):
    # This ensures that even if auth_service.py has hardcoded defaults,
    # the tests use consistent, test-specific values.
    # If auth_service.py correctly loads from os.environ, these might not strictly be needed
    # but it makes tests more robust against changes in how auth_service.py gets its config.
    monkeypatch.setattr(auth_service, 'SECRET_KEY', "testsecretkeyforpytest_some_very_long_and_random_string_for_testing_jwt")
    monkeypatch.setattr(auth_service, 'ALGORITHM', "HS256")
    monkeypatch.setattr(auth_service, 'ACCESS_TOKEN_EXPIRE_MINUTES', 30)
    # Update local test constants to use the monkeypatched values
    global TEST_SECRET_KEY, TEST_ALGORITHM, TEST_ACCESS_TOKEN_EXPIRE_MINUTES
    TEST_SECRET_KEY = "testsecretkeyforpytest_some_very_long_and_random_string_for_testing_jwt"
    TEST_ALGORITHM = "HS256"
    TEST_ACCESS_TOKEN_EXPIRE_MINUTES = 30


def test_password_hashing():
    password = "testpassword123"
    hashed_password = auth_service.get_password_hash(password)
    assert hashed_password != password
    assert auth_service.verify_password(password, hashed_password) is True
    assert auth_service.verify_password("wrongpassword", hashed_password) is False

def test_create_access_token_structure_and_content():
    data = {"sub": "testuser@example.com", "custom_claim": "test_value"}
    token = auth_service.create_access_token(data)

    assert isinstance(token, str)
    parts = token.split('.')
    assert len(parts) == 3 # Standard JWT format: header.payload.signature

    payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
    assert payload["sub"] == data["sub"]
    assert payload["custom_claim"] == data["custom_claim"]
    assert "exp" in payload

    # Check that 'exp' is a future timestamp
    expected_expiry = datetime.now(timezone.utc) + timedelta(minutes=TEST_ACCESS_TOKEN_EXPIRE_MINUTES)
    # Allow a small delta for execution time variance
    assert payload["exp"] > (expected_expiry - timedelta(seconds=60)).timestamp()
    assert payload["exp"] < (expected_expiry + timedelta(seconds=60)).timestamp()

def test_create_access_token_with_custom_expiry():
    data = {"sub": "testuser_custom_expiry@example.com"}
    custom_delta = timedelta(minutes=60)
    token = auth_service.create_access_token(data, expires_delta=custom_delta)

    payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
    assert payload["sub"] == data["sub"]

    expected_expiry = datetime.now(timezone.utc) + custom_delta
    assert payload["exp"] > (expected_expiry - timedelta(seconds=10)).timestamp()
    assert payload["exp"] < (expected_expiry + timedelta(seconds=10)).timestamp()


def test_decode_access_token_valid():
    data = {"sub": "testuser_valid@example.com", "scope": "admin"}
    token = auth_service.create_access_token(data)

    decoded_payload = auth_service.decode_access_token(token)
    assert decoded_payload is not None
    assert decoded_payload["sub"] == data["sub"]
    assert decoded_payload["scope"] == data["scope"]

def test_decode_access_token_invalid_signature():
    data = {"sub": "testuser_invalid_sig@example.com"}
    token_correct_key = auth_service.create_access_token(data)

    # Tamper with the token or use a different key for decoding attempt in service
    # If decode_access_token uses a key different from TEST_SECRET_KEY, it should fail.
    # Here, we test if decode_access_token correctly handles a token signed by another key.

    # Create a token with a different secret key
    wrong_key_token = jwt.encode(
        data,
        "ANOTHER_COMPLETELY_DIFFERENT_SECRET_KEY",
        algorithm=TEST_ALGORITHM
    )
    assert auth_service.decode_access_token(wrong_key_token) is None

def test_decode_access_token_malformed():
    malformed_token = "this.is.not.a.jwt"
    assert auth_service.decode_access_token(malformed_token) is None

def test_decode_access_token_expired():
    # This test ensures that decode_access_token itself returns None for an expired token
    data = {"sub": "testuser_expired_internal@example.com"}
    # Create a token that is already expired
    # ACCESS_TOKEN_EXPIRE_MINUTES is 30 by default from monkeypatch
    # To make it expire, set expires_delta to a negative value
    expired_token = auth_service.create_access_token(data, expires_delta=timedelta(seconds=-1))

    # Wait for a moment to ensure current time is past expiry if delta is very small
    time.sleep(0.1)

    assert auth_service.decode_access_token(expired_token) is None

def test_decode_access_token_future_nbf(): # Not Before
    # python-jose doesn't automatically handle 'nbf' (Not Before) validation in jwt.decode by default
    # unless options={'verify_nbf': True} is passed. auth_service.decode_access_token doesn't do this.
    # So, a token with future 'nbf' would still decode if 'exp' and signature are fine.
    # This test is more about documenting behavior than strict pass/fail of nbf.
    nbf_time = datetime.now(timezone.utc) + timedelta(hours=1)
    data = {"sub": "test_nbf", "nbf": nbf_time.timestamp()}
    token_with_future_nbf = auth_service.create_access_token(data)

    decoded_payload = auth_service.decode_access_token(token_with_future_nbf)
    assert decoded_payload is not None # Standard decode won't fail on future nbf by default
    assert decoded_payload["sub"] == "test_nbf"

def test_decode_access_token_missing_sub():
    # Create token without 'sub' if possible, or with 'sub': None
    # The create_access_token function expects data to be a dict, usually with 'sub'
    # If 'sub' is missing, what happens? Let's assume create_access_token doesn't enforce 'sub'
    # For this test, let's craft such a token manually
    payload_no_sub = {
        "exp": (datetime.now(timezone.utc) + timedelta(minutes=TEST_ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp(),
        "some_other_claim": "value"
    }
    token_no_sub = jwt.encode(payload_no_sub, TEST_SECRET_KEY, algorithm=TEST_ALGORITHM)

    # decode_access_token itself doesn't care about 'sub', just returns the payload
    decoded = auth_service.decode_access_token(token_no_sub)
    assert decoded is not None
    assert "sub" not in decoded
    assert decoded["some_other_claim"] == "value"
```
