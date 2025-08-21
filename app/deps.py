from fastapi import HTTPException, Request, status

from .security import get_token_from_cookie
from .supabase_client import get_supabase_client


async def get_current_user(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    client = get_supabase_client(token)
    try:
        user = client.auth.get_user(token).user
    except Exception as exc:  # pragma: no cover - network failures
        raise HTTPException(status_code=401) from exc
    profile_resp = (
        client.table("profiles")
        .select("id, display_name, role, email")
        .eq("id", user.id)
        .single()
        .execute()
    )
    profile = profile_resp.data or {}
    return {"id": user.id, **profile}