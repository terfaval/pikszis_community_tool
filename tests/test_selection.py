import types

from app.services import selection


class FakeTable:
    def __init__(self, data):
        self.data = data

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def in_(self, *args, **kwargs):
        return self

    def execute(self):
        return types.SimpleNamespace(data=self.data)


class FakeClient:
    def table(self, name):
        if name == "questionnaires":
            return FakeTable([{"id": "Q1", "in_random_pool": True, "is_active": True}])
        if name == "questions":
            return FakeTable(
                [
                    {
                        "id": "q1",
                        "title": "A",
                        "instructions": "",
                        "qtype": "open_text",
                        "likert_variant": None,
                        "questionnaire_id": "Q1",
                        "in_random_pool": True,
                    },
                    {
                        "id": "q2",
                        "title": "B",
                        "instructions": "",
                        "qtype": "open_text",
                        "likert_variant": None,
                        "questionnaire_id": "Q1",
                        "in_random_pool": True,
                    },
                ]
            )
        if name == "answers":
            return FakeTable(
                [
                    {
                        "question_key": "q1",
                        "value": {"likert": 3},
                        "submissions": {"user_id": "u"},
                    }
                ]
            )
        if name == "mode_cooldowns":
            return FakeTable([])
        raise KeyError(name)


def test_random_selection_skips_answered():
    client = FakeClient()
    q = selection.get_random_question(client, "u")
    assert q["id"] == "q2"