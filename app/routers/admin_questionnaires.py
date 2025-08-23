from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from typing import Optional
from app.db.questionnaires import list_questionnaires
from app.db.questions import list_questions

# Feltételezzük, hogy van valamilyen auth dependency (példa):
def require_user(request: Request):
    # Ha van már meglévő auth logika, cseréld erre.
    if not getattr(request.state, "user", None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return request.state.user

router = APIRouter(prefix="/admin/q", tags=["admin-questionnaires"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
def admin_q_index(request: Request, user=Depends(require_user)):
    qs = list_questionnaires(active_only=False)
    return templates.TemplateResponse(
        "admin/questionnaires.html",
        {"request": request, "user": user, "questionnaires": qs}
    )

@router.get("/{questionnaire_id}")
def admin_q_detail(questionnaire_id: int, request: Request, user=Depends(require_user)):
    questions = list_questions(questionnaire_id)
    # egyszerű fejléchez kinyerünk név/desc-et a listából, ha van
    # (ha kell külön lekérdezés, bevezethető)
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
            "questions": questions
        }
    )
