import csv
from pathlib import Path

from supabase import create_client

from ...config import settings

DATA_DIR = Path(__file__).parent / "data"


def load_csv(name: str):
    path = DATA_DIR / name
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def upsert(client, table: str, rows: list[dict], conflict: str):
    if not rows:
        return
    client.table(table).upsert(rows, on_conflict=conflict).execute()


def main() -> None:
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

    questionnaires = load_csv("questionnaires.utf8.csv")
    upsert(client, "questionnaires", questionnaires, "id")

    questions = load_csv("questions.utf8.csv")
    for row in questions:
        options = row.get("options")
        qtype = row.get("qtype")
        if options and qtype not in {"single_choice", "multiple_choice"}:
            print(f"Warning: options present but qtype is {qtype}")
    upsert(client, "questions", questions, "id")

    likerts = load_csv("likert_types.csv")
    for row in likerts:
        qtype = row.get("qtype")
        lv = row.get("likert_variant")
        if qtype not in {"likert_1_4", "likert_1_5"} or not lv:
            print(f"Warning: bad likert row {row}")

    print("Import complete")


if __name__ == "__main__":
    main()