"""
UNIT TESTS
==========
Yeh tests chhote, isolated pieces of code ko test karte hain -
seedha function/class call karke, poori HTTP request cycle ke
bina. Yeh sabse fast tests hote hain aur exact logic pinpoint
karte hain ki kahan bug hai.
"""

import pytest
from pydantic import ValidationError
from fastapi import HTTPException

from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest
from app.dependencies import get_current_user
from tests.conftest import FakeUser, FakeUserResponse


# ---------------------------------------------------------
# Schema validation tests (Pydantic models)
# ---------------------------------------------------------

def test_register_request_valid_data():
    """Sahi email/password/optional fields ke saath schema pass hona chahiye"""
    data = RegisterRequest(email="test@example.com", password="test1234")
    assert data.email == "test@example.com"
    assert data.name is None
    assert data.phone is None


def test_register_request_with_optional_fields():
    """name aur phone diye jaayen toh woh bhi store hone chahiye"""
    data = RegisterRequest(
        email="test@example.com",
        password="test1234",
        name="Shahnawaz",
        phone="9876543210",
    )
    assert data.name == "Shahnawaz"
    assert data.phone == "9876543210"


def test_register_request_invalid_email_rejected():
    """Galat format ka email schema level pe hi reject hona chahiye"""
    with pytest.raises(ValidationError):
        RegisterRequest(email="not-an-email", password="test1234")


def test_login_request_requires_email_and_password():
    """Email/password missing hone pe ValidationError aana chahiye"""
    with pytest.raises(ValidationError):
        LoginRequest(email="test@example.com")  # password missing


def test_refresh_request_requires_token():
    with pytest.raises(ValidationError):
        RefreshRequest()  # refresh_token missing


# ---------------------------------------------------------
# get_current_user dependency tests (direct function call)
# ---------------------------------------------------------

def test_get_current_user_valid_token(mock_supabase_auth, valid_bearer_credentials):
    """Valid token diya jaaye toh user ki details sahi return honi chahiye"""
    fake_user = FakeUser(
        id="user-123",
        email="test@example.com",
        metadata={"full_name": "Shahnawaz", "phone_number": "9876543210"},
    )
    mock_supabase_auth.get_user.return_value = FakeUserResponse(user=fake_user)

    result = get_current_user(credentials=valid_bearer_credentials)

    assert result["user_id"] == "user-123"
    assert result["email"] == "test@example.com"
    assert result["name"] == "Shahnawaz"
    assert result["phone"] == "9876543210"


def test_get_current_user_invalid_token_raises_401(mock_supabase_auth, valid_bearer_credentials):
    """Agar Supabase user None return kare (invalid token), 401 aana chahiye"""
    mock_supabase_auth.get_user.return_value = FakeUserResponse(user=None)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=valid_bearer_credentials)

    assert exc_info.value.status_code == 401


def test_get_current_user_supabase_error_raises_401(mock_supabase_auth, valid_bearer_credentials):
    """Agar Supabase call hi exception de de (expired/malformed token), 401 aana chahiye"""
    mock_supabase_auth.get_user.side_effect = Exception("token expired")

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=valid_bearer_credentials)

    assert exc_info.value.status_code == 401


def test_get_current_user_missing_metadata_returns_none(mock_supabase_auth, valid_bearer_credentials):
    """Agar user ne signup ke waqt name/phone nahi diya tha, woh fields None honi chahiye (crash nahi)"""
    fake_user = FakeUser(id="user-456", email="noname@example.com", metadata={})
    mock_supabase_auth.get_user.return_value = FakeUserResponse(user=fake_user)

    result = get_current_user(credentials=valid_bearer_credentials)

    assert result["name"] is None
    assert result["phone"] is None
