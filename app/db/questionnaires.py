from typing import List, Dict, Any, Optional

from app.supabase_client import get_admin_client


def list_questionnaires(active_only: bool = False) -> List[Dict[str, Any]]:
    """Return questionnaires for the admin list."""

    sb = get_admin_client()
    query = sb.table("questionnaires").select(
        "id,title,description,estimated_duration_minutes,is_active,mode"
    )
    if active_only:
        query = query.eq("is_active", True)
    res = query.order("title").execute()
    rows = res.data or []
    for row in rows:
        row["length_minutes"] = row.get("estimated_duration_minutes")
    return rows


def get_questionnaire(qid: str) -> Optional[Dict[str, Any]]:
    """Load a single questionnaire by its ID."""

    sb = get_admin_client()
    res = (
        sb.table("questionnaires")
        .select(
            "id,title,description,estimated_duration_minutes,is_active,mode"
        )
        .eq("id", qid)
        .limit(1)
        .execute()
    )
    data = res.data or []
    if not data:
        return None
    row = data[0]
    row["length_minutes"] = row.get("estimated_duration_minutes")
    return row


def upsert_questionnaire(payload: Dict[str, Any]) -> Dict[str, Any]:
    sb = get_admin_client()
    res = (
        sb.table("questionnaires")
        .upsert(payload, on_conflict="id")
        .select("*")
        .execute()
    )
    if not res.data:
        raise RuntimeError("Upsert failed for questionnaires")
    return res.data[0]