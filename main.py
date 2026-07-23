from fastapi import FastAPI
from app.routers import auth

app = FastAPI(
    title="Auth API with Supabase",
    description="Email/Password authentication using FastAPI + Supabase",
    version="1.0.0",
)

# Auth routes yahan register ho rahe hain
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Auth API chal raha hai! /docs pe jaake test karo."}
