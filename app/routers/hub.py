from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.deps import get_current_user
from app.supabase_client import supabase

router = APIRouter()


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


@router.get("/app", response_class=HTMLResponse)
async def app_hub(request: Request, user=Depends(get_current_user)):
    templates = get_templates(request)
    result = (
        supabase.table("questionnaires")
        .select("*")
        .eq("is_active", True)
        .execute()
    )
    questionnaires = result.data or []

    return request.app.state.templates.TemplateResponse(
        "hub.html",
        {
            "request": request,
            "questionnaires": questionnaires,
            "user": user,
        },
    )