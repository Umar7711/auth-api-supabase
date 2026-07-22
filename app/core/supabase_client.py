from supabase import create_client, Client
from app.core.config import SUPABASE_URL, SUPABASE_KEY

# Ek hi Supabase client banaya jo poori app mein reuse hoga
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
