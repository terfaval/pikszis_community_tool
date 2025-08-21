from supabase import Client, create_client

from .config import settings


def get_supabase_client(access_token: str | None = None) -> Client:
    client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    if access_token:
        client.postgrest.auth(access_token)
    return client