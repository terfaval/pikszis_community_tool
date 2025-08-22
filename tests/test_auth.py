import types
import bcrypt
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.db import users


def register(client, email="a@b.c", password="pw", display_name="A"):
    r = client.get("/register")
    token = r.cookies.get("csrf_token")
    return client.post(
        "/register",
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
        "/login",
        data={"email": email, "password": password, "csrf_token": token},
        allow_redirects=False,
    )


def test_register_user():
    users.clear_users()
    client = TestClient(app)
    resp = register(client, "user@example.com", "secret", "User")
    assert resp.status_code == 302
    user = users.get_user_by_email("user@example.com")
    assert user is not None
    assert user["password_hash"] != "secret"
    assert bcrypt.checkpw(b"secret", user["password_hash"].encode())


def test_login_user():
    users.clear_users()
    client = TestClient(app)
    register(client, "login@example.com", "pw", "Login")
    resp = login(client, "login@example.com", "pw")
    assert resp.status_code == 302
    assert resp.cookies.get(settings.COOKIE_NAME)


def test_login_invalid():
    users.clear_users()
    client = TestClient(app)
    register(client, "bad@example.com", "good", "Bad")
    resp = login(client, "bad@example.com", "wrong")
    assert resp.status_code == 400


def test_protected_route(monkeypatch):
    users.clear_users()
    client = TestClient(app)

    class FakeTable:
        def select(self, *args, **kwargs):
            return self

        def eq(self, *args, **kwargs):
            return self

        def execute(self):
            return types.SimpleNamespace(data=[])

    class FakeClient:
        def table(self, name):
            return FakeTable()

    monkeypatch.setattr("app.routers.hub.get_supabase_client", lambda: FakeClient())
    register(client, "p@q.c", "pw", "PQ")
    resp = login(client, "p@q.c", "pw")
    cookie = resp.cookies.get(settings.COOKIE_NAME)

    unauth_client = TestClient(app)
    monkeypatch.setattr("app.routers.hub.get_supabase_client", lambda: FakeClient())
    r = unauth_client.get("/app")
    assert r.status_code == 401

    client.cookies.set(settings.COOKIE_NAME, cookie)
    r2 = client.get("/app")
    assert r2.status_code == 200