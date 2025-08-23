from typing import List, Dict, Any, Optional
from app.supabase_client import get_admin_client

def list_questions(questionnaire_id: int) -> List[Dict[str, Any]]:
    sb = get_admin_client()
    res = sb.table("questions").select(
        "id,questionnaire_id,ord,title,instructions,qtype,likert_variant,"
        "required,random_order,random_multi,in_random_pool,branch_rules,following"
    ).eq("questionnaire_id", questionnaire_id).order("ord").execute()
    return res.data or []

def get_question(qid: int) -> Optional[Dict[str, Any]]:
    sb = get_admin_client()
    res = sb.table("questions").select(
        "id,questionnaire_id,ord,title,instructions,qtype,likert_variant,"
        "required,random_order,random_multi,in_random_pool,branch_rules,following"
    ).eq("id", qid).limit(1).execute()
    rows = res.data or []
    return rows[0] if rows else None

def upsert_question(payload: Dict[str, Any]) -> Dict[str, Any]:
    sb = get_admin_client()
    res = sb.table("questions").upsert(payload, on_conflict="id").select("*").execute()
    if not res.data:
        raise RuntimeError("Upsert failed for questions")
    return res.data[0]
