import logging

from fastapi import APIRouter, Form, HTTPException, Request, Response
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


@router.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    display_name: str = Form(...),
    csrf_token: str = Form(...),
):
    if not validate_csrf(request, csrf_token):
        raise HTTPException(status_code=400, detail="Bad CSRF token")
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        user = users.create_user(email, password_hash, display_name)
    except Exception:
        logger.info("Registration failed for %s", email)
        raise HTTPException(status_code=400, detail="Email already registered")
    logger.info("Registered user %s", email)
    print(f"Welcome email to {email}")  # placeholder for future email sending
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


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
):
    if not validate_csrf(request, csrf_token):
        raise HTTPException(status_code=400, detail="Bad CSRF token")
    user = users.get_user_by_email(email)
    if not user or not bcrypt.checkpw(
        password.encode(), user["password_hash"].encode()
    ):
        logger.info("Login failed for %s", email)
        raise HTTPException(status_code=400, detail="Login failed")
    logger.info("Login succeeded for %s", email)
    response = RedirectResponse("/app", status_code=302)
    set_session(response, user["id"])
    return response


@router.post("/logout")
async def logout(response: Response):
    clear_session(response)
    return RedirectResponse("/login", status_code=302)