from fastapi import APIRouter, Request, Depends, Form, HTTPException, Body
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from typing import Optional, List

from app.db.questionnaires import (
    list_questionnaires,
    get_questionnaire,
    upsert_questionnaire,
)
from app.db.questions import list_questions, reorder_questions


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
    questions = list_questions(questionnaire_id)
    return templates.TemplateResponse(
        "admin/questionnaire_edit.html",
        {"request": request, "user": user, "q": q, "questions": questions},
    )


@router.post("/{questionnaire_id}/upsert_header")
def admin_q_upsert_header(
    questionnaire_id: str,
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(default=None),
    length_minutes: Optional[str] = Form(default=None),
    is_active: bool = Form(default=False),
    in_random_pool: bool = Form(default=False),
    user=Depends(require_user),
):
    payload = {
        "id": questionnaire_id,
        "title": title,
        "description": description,
        "estimated_duration_minutes": normalize_length_minutes(length_minutes),
        "is_active": is_active,
        "in_random_pool": in_random_pool,
    }
    upsert_questionnaire(payload)
    return RedirectResponse(
        f"/admin/q/{questionnaire_id}/edit", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/{questionnaire_id}/reorder")
def admin_q_reorder(
    questionnaire_id: str,
    ordered_ids: List[int] = Body(...),
    user=Depends(require_user),
):
    reorder_questions(questionnaire_id, ordered_ids)
    return {"success": True}


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
def admin_q_detail(questionnaire_id: str):
    return RedirectResponse(
        f"/admin/q/{questionnaire_id}/edit", status_code=status.HTTP_303_SEE_OTHER
    )