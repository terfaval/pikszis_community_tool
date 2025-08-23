from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from typing import Optional

from app.db.questionnaires import (
    list_questionnaires,
    get_questionnaire,
    upsert_questionnaire,
)
from app.db.questions import list_questions


def require_user(request: Request):
    if not getattr(request.state, "user", None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return request.state.user


router = APIRouter(prefix="/admin/q", tags=["admin-questionnaires"])
templates = Jinja2Templates(directory="app/templates")


def normalize_length_minutes(value: Optional[str]) -> Optional[int]:
    """Convert form input to int or ``None``."""

    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError:
        return None


@router.get("")
def admin_q_index(request: Request, user=Depends(require_user)):
    qs = list_questionnaires(active_only=False)
    return templates.TemplateResponse(
        "admin/questionnaires.html",
        {"request": request, "user": user, "questionnaires": qs},
    )


@router.get("/new")
def admin_q_new(request: Request, user=Depends(require_user)):
    return templates.TemplateResponse(
        "admin/questionnaire_form.html",
        {"request": request, "user": user, "q": {}},
    )


@router.get("/{questionnaire_id}/edit")
def admin_q_edit(questionnaire_id: str, request: Request, user=Depends(require_user)):
    q = get_questionnaire(questionnaire_id)
    if not q:
        raise HTTPException(status_code=404, detail="Questionnaire not found")
    return templates.TemplateResponse(
        "admin/questionnaire_form.html",
        {"request": request, "user": user, "q": q},
    )


@router.post("/upsert")
def admin_q_upsert(
    request: Request,
    id: Optional[str] = Form(default=None),
    title: str = Form(...),
    length_minutes: Optional[str] = Form(default=None),
    is_active: bool = Form(default=False),
    user=Depends(require_user),
):
    payload = {
        "title": title,
        "estimated_duration_minutes": normalize_length_minutes(length_minutes),
        "is_active": is_active,
    }
    if id:
        payload["id"] = id
    upsert_questionnaire(payload)
    return RedirectResponse("/admin/q", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{questionnaire_id}")
def admin_q_detail(questionnaire_id: str, request: Request, user=Depends(require_user)):
    questions = list_questions(questionnaire_id)
    qmeta = None
    for item in list_questionnaires():
        if item["id"] == questionnaire_id:
            qmeta = item
            break
    return templates.TemplateResponse(
        "admin/questions.html",
        {
            "request": request,
            "user": user,
            "questionnaire_id": questionnaire_id,
            "qmeta": qmeta,
            "questions": questions,
        },
    )