# Auth API — FastAPI + Supabase

Email/password authentication with access & refresh tokens, powered by Supabase.

## Setup

1. **Dependencies install karo:**
   ```bash
   pip install -r requirements.txt
   ```

2. **`.env` file banao:**
   ```bash
   .env
   ```
   Fir `.env` file kholo aur `SUPABASE_URL` aur `SUPABASE_KEY` daalo
   (Supabase Dashboard → Settings → API se milega).

3. **Server chalao:**
   ```bash
   uvicorn main:app --reload
   ```

4. **Docs kholo:** browser mein `http://127.0.0.1:8000/docs` — yahan har route ko directly test kar sakte ho.

## Endpoints

| Method | Route          | Kya karta hai                              | Auth chahiye? |
|--------|----------------|---------------------------------------------|---------------|
| POST   | `/auth/register` | Naya user sign up karta hai              | Nahi          |
| POST   | `/auth/login`     | Login karke access + refresh token deta hai | Nahi        |
| POST   | `/auth/refresh`   | Naya access token deta hai refresh token se | Nahi        |
| POST   | `/auth/logout`    | Session revoke karta hai                   | Haan          |
| GET    | `/auth/me`        | Current logged-in user ki details          | Haan          |

## Testing flow (Swagger UI `/docs` pe)

1. `/auth/register` call karo with `{"email": "test@example.com", "password": "test1234"}`
2. Response mein `access_token` milega — usse copy karo
3. Right side top pe **"Authorize"** button click karo, token paste karo
4. Ab `/auth/me` call karo — apni details dikhengi
5. `access_token` expire hone pe `/auth/refresh` call karo apne `refresh_token` ke saath, naya `access_token` milega
