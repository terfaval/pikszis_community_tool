import logging

from fastapi import HTTPException, Request, status

from .security import get_token_from_cookie, verify_session_cookie
from .supabase_client import get_admin_client

logger = logging.getLogger(__name__)


async def get_current_user(request: Request):
    token = get_token_from_cookie(request)
    accept = request.headers.get("accept", "")
    wants_html = "text/html" in accept or accept == "*/*"
    if not token:
        logger.info("No session cookie present")
        if wants_html:
            raise HTTPException(status_code=302, headers={"Location": "/login"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_id = verify_session_cookie(token)
    if not user_id:
        logger.info("Session verification failed")
        if wants_html:
            raise HTTPException(status_code=302, headers={"Location": "/login"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    admin = get_admin_client()
    result = admin.table("users").select("*").eq("id", user_id).execute()
    user = result.data[0] if result.data else None
    if not user:
        logger.info("User %s not found", user_id)
        if wants_html:
            raise HTTPException(status_code=302, headers={"Location": "/login"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {
        "id": user["id"],
        "email": user["email"],
        "display_name": user["display_name"],
        "is_admin": user.get("is_admin", False),
    }