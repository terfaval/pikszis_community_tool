import types
import uuid

import bcrypt
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.db import users
from app.main import app


class FakeTable:
    def __init__(self, storage):
        self.storage = storage
        self.op = None
        self.payload = None
        self.filters = []

    def insert(self, data):
        self.op = "insert"
        self.payload = data
        return self

    def select(self, *args, **kwargs):
        self.op = "select"
        return self

    def eq(self, key, value):
        self.filters.append(("eq", key, value))
        return self

    def delete(self):
        self.op = "delete"
        return self

    def neq(self, key, value):
        self.filters.append(("neq", key, value))
        return self

    def execute(self):
        if self.op == "insert":
            record = dict(self.payload)
            record.setdefault("id", str(uuid.uuid4()))
            self.storage.append(record)
            return types.SimpleNamespace(data=[record])
        if self.op == "select":
            result = self.storage
            for op, key, value in self.filters:
                if op == "eq":
                    result = [r for r in result if r.get(key) == value]
            return types.SimpleNamespace(data=result)
        if self.op == "delete":
            self.storage.clear()
            return types.SimpleNamespace(data=[])


class FakeSupabase:
    def __init__(self):
        self.users = []

    def table(self, name):
        if name == "users":
            return FakeTable(self.users)
        return FakeTable([])


@pytest.fixture(autouse=True)
def fake_supabase(monkeypatch):
    fake = FakeSupabase()
    monkeypatch.setattr("app.db.users.admin", fake)
    monkeypatch.setattr("app.deps.get_admin_client", lambda: fake)
    monkeypatch.setattr("app.routers.hub.supabase", fake)
    return fake


def register(client, email="a@b.c", password="pw", display_name="A"):
    r = client.get("/register")
    token = r.cookies.get("csrf_token")
    return client.post(
        "/auth/register",
        data={
            "email": email,
            "password": password,
            "display_name": display_name,
            "csrf_token": token,
        },
        allow_redirects=False,
    )


def login(client, email="a@b.c", password="pw"):
    r = client.get("/login")
    token = r.cookies.get("csrf_token")
    return client.post(
        "/auth/login",
        data={"email": email, "password": password, "csrf_token": token},
        allow_redirects=False,
    )


def test_auth_flow(fake_supabase):
    users.clear_users()
    client = TestClient(app)

    resp = register(client, "user@example.com", "secret", "User")
    assert resp.status_code == 302
    user = users.get_user_by_email("user@example.com")
    assert user is not None
    assert bcrypt.checkpw(b"secret", user["password_hash"].encode())

    resp2 = login(client, "user@example.com", "secret")
    assert resp2.status_code == 302
    cookie = resp2.cookies.get(settings.COOKIE_NAME)
    assert cookie

    client.cookies.set(settings.COOKIE_NAME, cookie)
    r = client.get("/app")
    assert r.status_code == 200


def test_login_invalid_password(fake_supabase):
    users.clear_users()
    client = TestClient(app)

    register(client, "user@example.com", "secret", "User")

    resp = login(client, "user@example.com", "wrong")
    assert resp.status_code == 200
    assert "Hibás jelszó" in resp.text


def test_login_csrf_failure(fake_supabase):
    users.clear_users()
    client = TestClient(app)

    register(client)

    # Intentionally provide bad CSRF token
    client.get("/auth/login")
    resp = client.post(
        "/login",
        data={"email": "a@b.c", "password": "pw", "csrf_token": "bad"},
        allow_redirects=False,
    )
    assert resp.status_code == 200
    assert "Érvénytelen kérés" in resp.text