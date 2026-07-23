from fastapi import APIRouter, HTTPException, Depends, status
from app.core.supabase_client import supabase
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    AuthResponse,
    UserResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from fastapi.security import HTTPAuthorizationCredentials
from app.dependencies import get_current_user  , bearer_scheme

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse)
def register(data: RegisterRequest):
    """
    Naya user email + password se sign up karta hai.
    Supabase khud password ko hash karke store karta hai.
    """
    try:
        # name/phone sirf DISPLAY ke liye metadata mein jaayenge -
        # yeh login credentials nahi hain, sirf record ke roop mein save honge
        metadata = {}
        if data.name:
            metadata["full_name"] = data.name
        if data.phone:
            metadata["phone_number"] = data.phone
        
        response = supabase.auth.sign_up(
            {
                "email": data.email,
                "password": data.password,
                "options": {"data": metadata} if metadata else {},
            }
        )

        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration fail hua, dobara try karo",
            )

        # Agar email confirmation ON hai, session None milega
        # (user ko pehle email verify karna padega, phir login karna hoga)
        if response.session is None:
            raise HTTPException(
                status_code=status.HTTP_201_CREATED,
                detail="Account ban gaya. Email verify karke login karo.",
            )
        user_meta = response.user.user_metadata or {}
        

        return AuthResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user_id=response.user.id,
            email=response.user.email,
            name=user_meta.get("full_name"),
            phone=user_meta.get("phone_number"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest):
    """
    Existing user email + password se login karta hai.
    Success pe access_token + refresh_token milta hai.
    """
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": data.email, "password": data.password}
        )

        return AuthResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user_id=response.user.id,
            email=response.user.email,
            name=user_meta.get("full_name"),
            phone=user_meta.get("phone_number"),
            
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ya password galat hai",
        )


@router.post("/refresh", response_model=AuthResponse)
def refresh_token(data: RefreshRequest):
    """
    Jab access_token expire ho jaye (15 min - 1 hour, Supabase default),
    is refresh_token ka use karke naya access_token milega
    bina user ko dobara login kiye.
    """
    try:
        response = supabase.auth.refresh_session(data.refresh_token)

        return AuthResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user_id=response.user.id,
            email=response.user.email,
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalid ya expire ho gaya, dobara login karo",
        )


@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    """
    User ko logout karta hai — Supabase side pe session revoke ho jata hai.
    """
    try:
        supabase.auth.sign_out()
        return {"message": "Logout ho gaya"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """
    PROTECTED ROUTE - Sirf valid access_token ke saath call ho sakta hai.
    Yeh route dikhata hai ki authentication kaise kaam karta hai.
    """
    return UserResponse(
        user_id=current_user["user_id"],
        email=current_user["email"],
        name=current_user.get("name"),
        phone=current_user.get("phone"),
        
    )

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    """
    Email pe reset link bhejta hai. Link click karne pe user
    frontend pe redirect hoga jahan naya password set karega.
    """
    try:
        supabase.auth.reset_password_for_email(
            data.email,
            {"redirect_to": "http://localhost:8000/docs"}  # apna frontend URL daalna
        )
        return {"message": "Reset link email pe bhej diya gaya"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    """
    Reset link se mile token (URL mein hoga) ko Bearer token ki tarah
    bhejo, naya password isse set ho jayega.
    """
    try:
        authed_client = get_authed_client(credentials.credentials)
        authed_client.auth.update_user({"password": data.new_password})
        return {"message": "Password successfully change ho gaya"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
