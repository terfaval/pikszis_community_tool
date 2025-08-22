from fastapi import HTTPException, Request, status

from .db import users
from .security import get_token_from_cookie, verify_session_cookie


async def get_current_user(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_id = verify_session_cookie(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = users.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {
        "id": user["id"],
        "email": user["email"],
        "display_name": user["display_name"],
    }