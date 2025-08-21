from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from ..deps import get_current_user
from ..security import get_token_from_cookie
from ..services import answers, selection, submissions
from ..supabase_client import get_supabase_client

router = APIRouter(prefix="/api")


def get_templates(request: Request):
    return request.app.state.templates


@router.get("/questions/random", response_class=HTMLResponse)
async def random_question(request: Request, user=Depends(get_current_user)):
    token = get_token_from_cookie(request)
    client = get_supabase_client(token)
    question = selection.get_random_question(client, user["id"])
    templates = get_templates(request)
    if not question:
        return templates.TemplateResponse(
            "random_question_card.html",
            {"request": request, "message": "Come back later"},
        )
    csrf = ""  # no CSRF for HTMX demo
    return templates.TemplateResponse(
        "random_question_card.html",
        {"request": request, "question": question, "csrf": csrf},
    )


@router.post("/answers", response_class=HTMLResponse)
async def submit_answer(
    request: Request,
    user=Depends(get_current_user),
    question_id: str = Form(...),
    qtype: str = Form(...),
    value: str = Form(None),
):
    token = get_token_from_cookie(request)
    client = get_supabase_client(token)
    sub = submissions.get_or_create_submission(client, user["id"], None, "random")
    normalized: dict
    if qtype.startswith("likert"):
        normalized = {"likert": int(value)}
    elif qtype == "open_text":
        normalized = {"text": value}
    else:
        normalized = {"raw": value}
    answers.insert_answer(client, sub["id"], question_id, normalized)
    return await random_question(request, user)


@router.post("/answers/skip", response_class=HTMLResponse)
async def skip_answer(
    request: Request, user=Depends(get_current_user), question_id: str = Form(...)
):
    token = get_token_from_cookie(request)
    client = get_supabase_client(token)
    sub = submissions.get_or_create_submission(client, user["id"], None, "random")
    answers.insert_answer(client, sub["id"], question_id, {"skipped": True})
    return await random_question(request, user)