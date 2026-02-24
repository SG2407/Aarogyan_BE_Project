
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Supabase client instance
from supabase import create_client, Client

supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

def get_supabase() -> Client:
    """Dependency to get Supabase client"""
    return supabase
