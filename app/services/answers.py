from typing import Any, Dict


def insert_answer(client, submission_id: str, question_id: str, value: Dict[str, Any]):
    payload = {
        "submission_id": submission_id,
        "question_key": question_id,
        "value": value,
    }
    client.table("answers").insert(payload).execute()