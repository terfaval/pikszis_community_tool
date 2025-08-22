import logging
from typing import Any, Dict, Optional

from app.supabase_client import supabase

logger = logging.getLogger(__name__)


def create_user(email: str, password_hash: str, display_name: str) -> Dict[str, Any]:
    data = {
        "email": email,
        "password_hash": password_hash,
        "display_name": display_name,
    }
    logger.info("Creating user %s", email)
    result = supabase.table("users").insert(data).execute()
    if not result.data:
        raise RuntimeError("User insert failed")
    return result.data[0]


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    result = supabase.table("users").select("*").eq("email", email).execute()
    return result.data[0] if result.data else None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    result = supabase.table("users").select("*").eq("id", user_id).execute()
    return result.data[0] if result.data else None


def clear_users() -> None:
    # Delete all users (used in tests)
    supabase.table("users").delete().neq("id", "0").execute()
    