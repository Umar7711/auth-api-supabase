from pydantic import BaseModel, EmailStr
from typing import Optional



class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
