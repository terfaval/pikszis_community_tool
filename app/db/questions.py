from typing import List, Dict, Any, Optional

from app.supabase_client import get_admin_client


def list_questions(questionnaire_id: int) -> List[Dict[str, Any]]:
    sb = get_admin_client()
    res = (
        sb.table("questions")
        .select(
            "id,questionnaire_id,ord,priority,title,qtype,"
            "random_order,random_answer,branch_rules"
        )
        .eq("questionnaire_id", questionnaire_id)
        .order("ord")
        .execute()
    )
    return res.data or []


def get_question(qid: int) -> Optional[Dict[str, Any]]:
    sb = get_admin_client()
    res = (
        sb.table("questions")
        .select(
            "id,questionnaire_id,ord,priority,title,qtype,"
            "random_order,random_answer,branch_rules"
        )
        .eq("id", qid)
        .limit(1)
        .execute()
    )
    rows = res.data or []
    return rows[0] if rows else None


def upsert_question(payload: Dict[str, Any]) -> Dict[str, Any]:
    sb = get_admin_client()
    res = sb.table("questions").upsert(payload, on_conflict="id").select("*").execute()
    if not res.data:
        raise RuntimeError("Upsert failed for questions")
    return res.data[0]


def reorder_questions(questionnaire_id: int, ordered_ids: List[int]) -> None:
    """Update ``ord`` fields for questions in the given questionnaire.

    The first ID in ``ordered_ids`` will receive ``ord`` 1, the second ``ord`` 2,
    and so on. Extra IDs are ignored and missing IDs are left untouched.
    """

    sb = get_admin_client()
    payload = [
        {"id": qid, "questionnaire_id": questionnaire_id, "ord": idx + 1}
        for idx, qid in enumerate(ordered_ids)
    ]
    if payload:
        sb.table("questions").upsert(payload, on_conflict="id").execute()


def list_question_options(question_id: int) -> List[Dict[str, Any]]:
    """Return options for a question ordered by ``ord``."""

    sb = get_admin_client()
    res = (
        sb.table("question_options")
        .select("id,question_id,ord,label,value")
        .eq("question_id", question_id)
        .order("ord")
        .execute()
    )
    return res.data or []


def upsert_question_option(payload: Dict[str, Any]) -> Dict[str, Any]:
    sb = get_admin_client()
    res = (
        sb.table("question_options")
        .upsert(payload, on_conflict="id")
        .select("*")
        .execute()
    )
    if not res.data:
        raise RuntimeError("Upsert failed for question_options")
    return res.data[0]


def replace_question_options(question_id: int, options: List[Dict[str, Any]]) -> None:
    """Replace all options for ``question_id`` with the given list."""

    sb = get_admin_client()
    sb.table("question_options").delete().eq("question_id", question_id).execute()

    payload = [
        {
            "question_id": question_id,
            "ord": idx + 1,
            "label": opt.get("label"),
            "value": opt.get("value"),
        }
        for idx, opt in enumerate(options)
        if opt.get("label")
    ]
    if payload:
        sb.table("question_options").insert(payload).execute()


def reorder_question_options(question_id: int, ordered_ids: List[int]) -> None:
    """Update ``ord`` fields for the given option IDs."""

    sb = get_admin_client()
    payload = [
        {"id": oid, "question_id": question_id, "ord": idx + 1}
        for idx, oid in enumerate(ordered_ids)
    ]
    if payload:
        sb.table("question_options").upsert(payload, on_conflict="id").execute()