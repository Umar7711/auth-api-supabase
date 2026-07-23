"""
INTEGRATION TESTS
=================
Yeh tests poori FastAPI app ke against real jaisi HTTP requests
bhejte hain (routing + validation + dependency injection + response
sab ek saath test hota hai) - jaise koi asli client (Postman/frontend)
in endpoints ko call kar raha ho. Sirf Supabase ki asli network call
mock ki gayi hai, baaki poora FastAPI stack real hai.
"""

from tests.conftest import FakeUser, FakeSession, FakeAuthResponse, FakeUserResponse


# ---------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------

def test_register_success(client, mock_supabase_auth):
    fake_user = FakeUser(id="user-1", email="new@example.com")
    mock_supabase_auth.sign_up.return_value = FakeAuthResponse(
        user=fake_user, session=FakeSession()
    )

    response = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "test1234"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "new@example.com"
    assert body["access_token"] == "fake-access-token"
    assert body["refresh_token"] == "fake-refresh-token"


def test_register_with_name_and_phone_saved_as_metadata(client, mock_supabase_auth):
    """Register mein name/phone diya jaaye toh Supabase ko metadata ke roop mein bhejna chahiye"""
    fake_user = FakeUser(
        id="user-2",
        email="withname@example.com",
        metadata={"full_name": "Shahnawaz", "phone_number": "9876543210"},
    )
    mock_supabase_auth.sign_up.return_value = FakeAuthResponse(
        user=fake_user, session=FakeSession()
    )

    response = client.post(
        "/auth/register",
        json={
            "email": "withname@example.com",
            "password": "test1234",
            "name": "Shahnawaz",
            "phone": "9876543210",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Shahnawaz"
    assert body["phone"] == "9876543210"

    # Verify karo ki sign_up ko sahi metadata ke saath call kiya gaya tha
    call_args = mock_supabase_auth.sign_up.call_args[0][0]
    assert call_args["options"]["data"]["full_name"] == "Shahnawaz"
    assert call_args["options"]["data"]["phone_number"] == "9876543210"


def test_register_missing_password_returns_422(client, mock_supabase_auth):
    """Pydantic validation fail ho toh FastAPI khud hi 422 dega, route code chalega hi nahi"""
    response = client.post("/auth/register", json={"email": "test@example.com"})
    assert response.status_code == 422


def test_register_no_session_returns_error(client, mock_supabase_auth):
    """Email confirmation ON ho toh session None aata hai - humara code isko handle kare"""
    fake_user = FakeUser(id="user-3", email="pending@example.com")
    mock_supabase_auth.sign_up.return_value = FakeAuthResponse(user=fake_user, session=None)

    response = client.post(
        "/auth/register",
        json={"email": "pending@example.com", "password": "test1234"},
    )

    assert response.status_code == 201


def test_register_supabase_failure_returns_400(client, mock_supabase_auth):
    """Agar Supabase khud error de (jaise duplicate email), 400 return hona chahiye"""
    mock_supabase_auth.sign_up.side_effect = Exception("User already registered")

    response = client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "test1234"},
    )

    assert response.status_code == 400


# ---------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------

def test_login_success(client, mock_supabase_auth):
    fake_user = FakeUser(id="user-1", email="test@example.com")
    mock_supabase_auth.sign_in_with_password.return_value = FakeAuthResponse(
        user=fake_user, session=FakeSession()
    )

    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "test1234"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "fake-access-token"


def test_login_wrong_credentials_returns_401(client, mock_supabase_auth):
    """Galat email/password pe Supabase exception dega - humein 401 return karna chahiye"""
    mock_supabase_auth.sign_in_with_password.side_effect = Exception("Invalid credentials")

    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401


# ---------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------

def test_refresh_token_success(client, mock_supabase_auth):
    fake_user = FakeUser(id="user-1", email="test@example.com")
    mock_supabase_auth.refresh_session.return_value = FakeAuthResponse(
        user=fake_user,
        session=FakeSession(access_token="new-access-token", refresh_token="new-refresh-token"),
    )

    response = client.post(
        "/auth/refresh", json={"refresh_token": "old-refresh-token"}
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "new-access-token"


def test_refresh_token_expired_returns_401(client, mock_supabase_auth):
    mock_supabase_auth.refresh_session.side_effect = Exception("Refresh token expired")

    response = client.post(
        "/auth/refresh", json={"refresh_token": "expired-token"}
    )

    assert response.status_code == 401


# ---------------------------------------------------------
# GET /auth/me (protected route)
# ---------------------------------------------------------

def test_get_me_without_token_returns_403(client, mock_supabase_auth):
    """Bina Authorization header ke protected route call karo - FastAPI khud reject karega"""
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_get_me_with_valid_token(client, mock_supabase_auth):
    fake_user = FakeUser(
        id="user-1", email="test@example.com", metadata={"full_name": "Shahnawaz"}
    )
    mock_supabase_auth.get_user.return_value = FakeUserResponse(user=fake_user)

    response = client.get(
        "/auth/me", headers={"Authorization": "Bearer fake-access-token"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "test@example.com"
    assert body["name"] == "Shahnawaz"


def test_get_me_with_invalid_token_returns_401(client, mock_supabase_auth):
    mock_supabase_auth.get_user.side_effect = Exception("invalid token")

    response = client.get(
        "/auth/me", headers={"Authorization": "Bearer garbage-token"}
    )

    assert response.status_code == 401


# ---------------------------------------------------------
# POST /auth/logout (protected route)
# ---------------------------------------------------------

def test_logout_success(client, mock_supabase_auth):
    fake_user = FakeUser(id="user-1", email="test@example.com")
    mock_supabase_auth.get_user.return_value = FakeUserResponse(user=fake_user)
    mock_supabase_auth.sign_out.return_value = None

    response = client.post(
        "/auth/logout", headers={"Authorization": "Bearer fake-access-token"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Logout ho gaya"
