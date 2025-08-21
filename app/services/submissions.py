from typing import Optional


def get_or_create_submission(
    client, user_id: str, questionnaire_id: Optional[str], mode: str
):
    query = (
        client.table("submissions")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "draft")
        .eq("mode", mode)
    )
    if questionnaire_id:
        query = query.eq("questionnaire_id", questionnaire_id)
    else:
        query = query.is_("questionnaire_id", None)
    existing = query.limit(1).execute().data
    if existing:
        return existing[0]
    insert = {
        "questionnaire_id": questionnaire_id,
        "user_id": user_id,
        "mode": mode,
        "status": "draft",
    }
    created = client.table("submissions").insert(insert).execute().data[0]
    return created