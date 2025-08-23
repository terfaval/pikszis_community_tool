import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import bcrypt

from ..db import users
from ..security import (
    clear_session,
    generate_csrf_token,
    set_csrf,
    set_session,
    validate_csrf,
)

router = APIRouter()

logger = logging.getLogger(__name__)


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    templates = get_templates(request)
    token = generate_csrf_token()
    response = templates.TemplateResponse(
        "auth_register.html", {"request": request, "csrf": token}
    )
    set_csrf(response, token)
    return response


@router.post("/auth/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    display_name: str = Form(...),
    csrf_token: str = Form(...),
):
    templates = get_templates(request)

    if not validate_csrf(request, csrf_token):
        logger.info("Registration CSRF validation failed for %s", email)
        token = generate_csrf_token()
        response = templates.TemplateResponse(
            "auth_register.html",
            {
                "request": request,
                "csrf": token,
                "error": "Érvénytelen kérés. Próbáld újra.",
            },
        )
        set_csrf(response, token)
        return response

    email = email.strip()
    logger.info("Registration attempt for %s", email)
    if users.get_user_by_email(email):
        logger.info("Registration email exists %s", email)
        token = generate_csrf_token()
        response = templates.TemplateResponse(
            "auth_register.html",
            {
                "request": request,
                "csrf": token,
                "error": "Ezzel az e-mail címmel már van felhasználó. Jelentkezz be.",
            },
        )
        set_csrf(response, token)
        return response

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = users.create_user(email, password_hash, display_name)
    logger.info("Registration succeeded for %s", email)

    response = RedirectResponse("/app", status_code=302)
    set_session(response, user["id"])
    return response


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    templates = get_templates(request)
    token = generate_csrf_token()
    response = templates.TemplateResponse(
        "auth_login.html", {"request": request, "csrf": token}
    )
    set_csrf(response, token)
    return response


@router.post("/auth/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
):
    templates = get_templates(request)

    if not validate_csrf(request, csrf_token):
        logger.info("Login CSRF validation failed for %s", email)
        token = generate_csrf_token()
        response = templates.TemplateResponse(
            "auth_login.html",
            {
                "request": request,
                "csrf": token,
                "error": "Érvénytelen kérés. Próbáld újra.",
            },
        )
        set_csrf(response, token)
        return response

    email = email.strip()
    logger.info("Login attempt for %s", email)

    user = users.get_user_by_email(email)
    if not user:
        logger.info("Login failed, no user for %s", email)
        token = generate_csrf_token()
        response = templates.TemplateResponse(
            "auth_login.html",
            {
                "request": request,
                "csrf": token,
                "error": "Ezzel az e-mail címmel nincs felhasználó. Regisztrálj.",
            },
        )
        set_csrf(response, token)
        return response

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        logger.info("Login failed, bad password for %s", email)
        token = generate_csrf_token()
        response = templates.TemplateResponse(
            "auth_login.html",
            {
                "request": request,
                "csrf": token,
                "error": "Hibás jelszó.",
            },
        )
        set_csrf(response, token)
        return response

    logger.info("Login succeeded for %s", email)
    response = RedirectResponse("/app", status_code=302)
    set_session(response, user["id"])
    return response


@router.post("/login")
async def login_alias(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
):
    """Backward compatible login endpoint used in older clients/tests."""

    return await login(request, email, password, csrf_token)


@router.post("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=302)
    clear_session(response)
    return response
