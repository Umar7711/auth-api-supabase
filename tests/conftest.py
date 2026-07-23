import os

# IMPORTANT: env vars real Supabase se connect hone se pehle set karne
# padte hain, warna app/core/config.py import hote hi crash ho jayega
# (yeh values fake hain, kabhi real Supabase se contact nahi hoga
# kyunki hum har test mein supabase.auth ko mock kar denge)
os.environ.setdefault("SUPABASE_URL", "https://fake-project.supabase.co")
os.environ.setdefault(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYW5vbiJ9.fake-signature-for-tests-only",
)

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials

from main import app
from app.core import supabase_client


class FakeUser:
    """Supabase ke asli User object jaisa hi banaya gaya fake object"""

    def __init__(self, id="user-123", email="test@example.com", metadata=None):
        self.id = id
        self.email = email
        self.user_metadata = metadata or {}


class FakeSession:
    """Supabase ke asli Session object jaisa fake object (tokens ke liye)"""

    def __init__(self, access_token="fake-access-token", refresh_token="fake-refresh-token"):
        self.access_token = access_token
        self.refresh_token = refresh_token


class FakeAuthResponse:
    """sign_up / sign_in_with_password / refresh_session sab isi shape ka response dete hain"""

    def __init__(self, user=None, session=None):
        self.user = user
        self.session = session


class FakeUserResponse:
    """get_user() ka response is shape ka hota hai"""

    def __init__(self, user=None):
        self.user = user


@pytest.fixture
def client():
    """FastAPI TestClient - poori app ke against real jaisi HTTP requests bhejta hai"""
    return TestClient(app)


@pytest.fixture
def mock_supabase_auth(monkeypatch):
    """
    Yeh fixture asli Supabase se connection replace karke ek MagicMock
    laga deta hai. Isse:
    - Koi real network call nahi hoti (tests fast aur reliable rehte hain)
    - Hum control kar sakte hain ki "Supabase" ne kya return kiya
      (success ho ya failure, dono scenarios test kar sakte hain)

    supabase_client.supabase object app ke saare modules (routers,
    dependencies) mein SAME reference se import hota hai, isliye ek
    hi jagah patch karne se sab jagah effect hota hai.
    """
    mock_auth = MagicMock()
    monkeypatch.setattr(supabase_client.supabase, "auth", mock_auth)
    return mock_auth


@pytest.fixture
def valid_bearer_credentials():
    """Ek fake 'Authorization: Bearer <token>' header simulate karta hai"""
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake-access-token")
