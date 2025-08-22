from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from ..config import settings
from ..deps import get_current_user
from ..supabase_client import get_supabase_client

router = APIRouter()


def get_templates(request: Request):
    return request.app.state.templates


def fetch_questionnaires(client):
    data = (
        client.table("questionnaires")
        .select("id,title,description,is_active")
        .eq("is_active", True)
        .execute()
        .data
        or []
    )
    recommended = [q for q in data if q["id"] in settings.CORE_QUESTIONNAIRE_IDS]
    others = [q for q in data if q["id"] not in settings.CORE_QUESTIONNAIRE_IDS]
    recommended.sort(key=lambda q: settings.CORE_QUESTIONNAIRE_IDS.index(q["id"]))
    others.sort(key=lambda q: (not q["is_active"], q["title"]))
    return recommended + others


@router.get("/app", response_class=HTMLResponse)
async def hub_page(request: Request, user=Depends(get_current_user)):
    templates = get_templates(request)
    client = get_supabase_client()
    questionnaires = fetch_questionnaires(client)
    return templates.TemplateResponse(
        "hub.html", {"request": request, "user": user, "questionnaires": questionnaires}
    )


@router.get("/embed", response_class=HTMLResponse)
async def embed_page(request: Request, user=Depends(get_current_user)):
    templates = get_templates(request)
    client = get_supabase_client()
    questionnaires = fetch_questionnaires(client)
    return templates.TemplateResponse(
        "embed_hub.html",
        {"request": request, "user": user, "questionnaires": questionnaires},
    )