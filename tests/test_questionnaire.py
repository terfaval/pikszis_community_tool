import types

from app.routers import questionnaire_api as qa


class FakeTable:
    def __init__(self, data):
        self.data = data

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        self.data = sorted(self.data, key=lambda d: d["ord"])
        return self

    def execute(self):
        return types.SimpleNamespace(data=self.data)


class FakeClient:
    def __init__(self, data):
        self.data = data

    def table(self, name):
        return FakeTable(self.data)


def test_question_ordering_by_ord():
    data = [
        {"id": "q1", "ord": 2, "random_order": False},
        {"id": "q2", "ord": 1, "random_order": False},
    ]
    client = FakeClient(data)
    qs = qa.load_questions(client, "Q1")
    assert [q["id"] for q in qs] == ["q2", "q1"]


def test_question_random_order():
    data = [
        {"id": "q1", "ord": 1, "random_order": True},
        {"id": "q2", "ord": 2, "random_order": True},
    ]
    client = FakeClient(data)
    qs = qa.load_questions(client, "Q1")
    assert [q["id"] for q in qs] in (["q1", "q2"], ["q2", "q1"])  # shuffled