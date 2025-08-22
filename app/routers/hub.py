from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from app.deps import get_current_user
from app.supabase_client import supabase
from app.templates import templates

router = APIRouter()


@router.get("/app", response_class=HTMLResponse)
async def app_hub(request: Request, user=Depends(get_current_user)):
    result = supabase.table("questionnaires").select("*").eq("is_active", True).execute()
    questionnaires = result.data or []

    return templates.TemplateResponse(
        "hub.html",
        {
            "request": request,
            "questionnaires": questionnaires,
            "user": user,
        },
    )