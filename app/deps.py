import logging

from fastapi import HTTPException, Request, status

from .db import users
from .security import get_token_from_cookie, verify_session_cookie

logger = logging.getLogger(__name__)


async def get_current_user(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        logger.info("No session cookie present")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_id = verify_session_cookie(token)
    if not user_id:
        logger.info("Session verification failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = users.get_user_by_id(user_id)
    if not user:
        logger.info("User %s not found", user_id)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {
        "id": user["id"],
        "email": user["email"],
        "display_name": user["display_name"],
    }