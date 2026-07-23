from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase_client import supabase

# Yeh scheme "Authorization: Bearer <token>" header ko read karega
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """
    Har protected route pe yeh function chalega.
    Access token nikalega header se, Supabase se verify karayega,
    aur agar valid hai toh user ki details return karega.
    """
    token = credentials.credentials

    try:
        # Supabase khud check karega ki token valid hai ya expire ho gaya
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid ya expired token",
            )
        user_meta = user.user_metadata or {}

        return {"user_id": user.id,
                "email": user.email,
                "name": user_meta.get("full_name"),
                "phone": user_meta.get("phone_number"),
                }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ya expired token",
        )
