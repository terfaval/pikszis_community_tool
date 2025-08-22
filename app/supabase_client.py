from supabase import Client, create_client

from .config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def get_supabase_client(access_token: str | None = None) -> Client:
    if access_token:
        supabase.postgrest.auth(access_token)
    return supabase