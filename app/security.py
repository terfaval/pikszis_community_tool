import secrets

from fastapi import Request, Response

SESSION_COOKIE = "sb_access_token"
CSRF_COOKIE = "csrf_token"


def set_session(response: Response, access_token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        access_token,
        httponly=True,
        samesite="lax",
    )


def clear_session(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE)


def get_token_from_cookie(request: Request) -> str | None:
    return request.cookies.get(SESSION_COOKIE)


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(16)


def set_csrf(response: Response, token: str) -> None:
    response.set_cookie(CSRF_COOKIE, token, httponly=False, samesite="lax")


def validate_csrf(request: Request, token: str) -> bool:
    return request.cookies.get(CSRF_COOKIE) == token