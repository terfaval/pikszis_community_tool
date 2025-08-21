import random

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..deps import get_current_user
from ..security import get_token_from_cookie
from ..services import answers, submissions
from ..supabase_client import get_supabase_client

router = APIRouter()


def get_templates(request: Request):
    return request.app.state.templates


def load_questions(client, questionnaire_id: str):
    questions = (
        client.table("questions")
        .select("id,title,instructions,qtype,likert_variant,ord,random_order")
        .eq("questionnaire_id", questionnaire_id)
        .order("ord")
        .execute()
        .data
        or []
    )
    if questions and questions[0].get("random_order"):
        rnd = random.Random(questionnaire_id)
        rnd.shuffle(questions)
    return questions


@router.get("/q/{qid}", response_class=HTMLResponse)
async def run_questionnaire(qid: str, request: Request, user=Depends(get_current_user)):
    templates = get_templates(request)
    token = get_token_from_cookie(request)
    client = get_supabase_client(token)
    sub = submissions.get_or_create_submission(client, user["id"], qid, "targeted")
    questions = load_questions(client, qid)
    idx = sub.get("current_ord", 0)
    if idx >= len(questions):
        client.table("submissions").update({"status": "submitted"}).eq(
            "id", sub["id"]
        ).execute()
        return templates.TemplateResponse(
            "questionnaire_runner.html", {"request": request, "completed": True}
        )
    question = questions[idx]
    return templates.TemplateResponse(
        "questionnaire_runner.html",
        {
            "request": request,
            "question": question,
            "progress": (idx + 1, len(questions)),
            "qid": qid,
        },
    )


@router.post("/q/{qid}/answer")
async def answer_question(
    qid: str,
    request: Request,
    user=Depends(get_current_user),
    question_id: str = Form(...),
    qtype: str = Form(...),
    value: str | None = Form(None),
    skip: str | None = Form(None),
):
    token = get_token_from_cookie(request)
    client = get_supabase_client(token)
    sub = submissions.get_or_create_submission(client, user["id"], qid, "targeted")
    if skip:
        answers.insert_answer(client, sub["id"], question_id, {"skipped": True})
    else:
        if qtype.startswith("likert"):
            normalized = {"likert": int(value)}
        elif qtype == "open_text":
            normalized = {"text": value}
        else:
            normalized = {"raw": value}
        answers.insert_answer(client, sub["id"], question_id, normalized)
    client.table("submissions").update(
        {"current_ord": sub.get("current_ord", 0) + 1}
    ).eq("id", sub["id"]).execute()
    return RedirectResponse(f"/q/{qid}", status_code=302)