from fastapi import APIRouter, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..security import (
    clear_session,
    generate_csrf_token,
    set_csrf,
    set_session,
    validate_csrf,
)
from ..supabase_client import get_supabase_client

router = APIRouter()


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
    client = get_supabase_client()
    resp = client.auth.sign_up(
        {
            "email": email,
            "password": password,
            "options": {"data": {"display_name": display_name}},
        }
    )
    if not resp.session:
        raise HTTPException(status_code=400, detail="Registration failed")
    response = RedirectResponse("/app", status_code=302)
    set_session(response, resp.session.access_token)
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
    client = get_supabase_client()
    data = client.auth.sign_in_with_password({"email": email, "password": password})
    if not data.session:
        raise HTTPException(status_code=400, detail="Login failed")
    response = RedirectResponse("/app", status_code=302)
    set_session(response, data.session.access_token)
    return response


@router.post("/logout")
async def logout(response: Response):
    clear_session(response)
    return RedirectResponse("/login", status_code=302)