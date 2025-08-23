from typing import List, Dict, Any, Optional
from app.supabase_client import get_admin_client


def list_questionnaires(active_only: bool = False) -> List[Dict[str, Any]]:
    sb = get_admin_client()
    query = sb.table("questionnaires").select(
        "id,title,description,intro_text,is_active,in_random_pool"
    )
    if active_only:
        query = query.eq("is_active", True)
    res = query.order("title").execute()
    return res.data or []

def upsert_questionnaire(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    payload példákul:
    {
      "id": 1,  # opcionális
      "title": "Lakóközösségi igényfelmérés",
      "description": "Rövid leírás az admin listához...",
      "intro_text": "Bevezető a kitöltőknek...",
      "is_active": True,
      "in_random_pool": True
    }
    """
    sb = get_admin_client()
    res = sb.table("questionnaires").upsert(payload, on_conflict="id").select("*").execute()
    if not res.data:
        raise RuntimeError("Upsert failed for questionnaires")
    return res.data[0]
