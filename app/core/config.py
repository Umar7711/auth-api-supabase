import os
from dotenv import load_dotenv

# .env file se variables load karo
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL aur SUPABASE_KEY .env file mein set karo. "
        ".env.example ko copy karke .env banao aur values daalo."
    )
