import logging
import secrets

from fastapi import Request, Response
from itsdangerous import BadSignature, URLSafeSerializer

from .config import settings

SESSION_COOKIE = settings.COOKIE_NAME
CSRF_COOKIE = "csrf_token"
_serializer = URLSafeSerializer(settings.SECRET_KEY, salt="session")
logger = logging.getLogger(__name__)


def sign_session_cookie(user_id: str) -> str:
    return _serializer.dumps({"user_id": user_id})


def verify_session_cookie(token: str) -> str | None:
    try:
        data = _serializer.loads(token)
    except BadSignature:
        logger.info("Invalid session cookie signature")
        return None
    return data.get("user_id")


def set_session(response: Response, user_id: str) -> None:
    token = sign_session_cookie(user_id)
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,secure=settings.COOKIE_SECURE,
        max_age=settings.SESSION_MAX_AGE,
        path="/",
    )
    logger.info("Set session cookie for user %s", user_id)


def clear_session(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE)
    logger.info("Cleared session cookie")


def get_token_from_cookie(request: Request) -> str | None:
    return request.cookies.get(SESSION_COOKIE)


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(16)


def set_csrf(response: Response, token: str) -> None:
    response.set_cookie(CSRF_COOKIE, token, httponly=False, samesite="lax")


def validate_csrf(request: Request, token: str) -> bool:
    return request.cookies.get(CSRF_COOKIE) == token