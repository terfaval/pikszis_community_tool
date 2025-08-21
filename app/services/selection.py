import datetime as dt
import random
from typing import Any, Dict, List

# TODO: replace with SQL function when dataset grows


def get_random_question(client, user_id: str) -> Dict[str, Any] | None:
    now = dt.datetime.utcnow().isoformat()
    cd = (
        client.table("mode_cooldowns")
        .select("hidden_until")
        .eq("user_id", user_id)
        .eq("mode", "random")
        .order("hidden_until", desc=True)
        .limit(1)
        .execute()
        .data
    )
    if cd and cd[0]["hidden_until"] and cd[0]["hidden_until"] > now:
        return None

    questionnaires = (
        client.table("questionnaires")
        .select("id,in_random_pool,is_active")
        .eq("is_active", True)
        .execute()
        .data
        or []
    )
    allowed_qids = [q["id"] for q in questionnaires if q.get("in_random_pool", True)]

    questions = (
        client.table("questions")
        .select("id,title,instructions,qtype,likert_variant,questionnaire_id")
        .eq("in_random_pool", True)
        .in_("questionnaire_id", allowed_qids)
        .limit(200)
        .execute()
        .data
        or []
    )

    answered_rows = (
        client.table("answers")
        .select("question_key,value,submission_id,submissions!inner(user_id)")
        .eq("submissions.user_id", user_id)
        .execute()
        .data
        or []
    )
    answered = {
        row["question_key"]
        for row in answered_rows
        if row.get("value", {}).get("skipped") is not True
    }
    skipped = {
        row["question_key"]
        for row in answered_rows
        if row.get("value", {}).get("skipped") is True
    }

    unseen = [
        q for q in questions if q["id"] not in answered and q["id"] not in skipped
    ]
    skipped_list = [q for q in questions if q["id"] in skipped]

    pool: List[Dict[str, Any]] = unseen + skipped_list
    if not pool:
        return None

    weights = [1.0 if q in unseen else 0.5 for q in pool]
    choice = random.choices(pool, weights=weights, k=1)[0]
    return choice