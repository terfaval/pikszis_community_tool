import types

from fastapi.testclient import TestClient

from app.main import app


class FakeSession:
    access_token = "token"


class FakeAuth:
    def sign_in_with_password(self, creds):
        return types.SimpleNamespace(session=FakeSession())

    def sign_up(self, creds):
        return types.SimpleNamespace(session=FakeSession())


class FakeClient:
    auth = FakeAuth()


def fake_get_client(*args, **kwargs):
    return FakeClient()


def test_login_sets_cookie(monkeypatch):
    monkeypatch.setattr("app.routers.auth.get_supabase_client", fake_get_client)
    client = TestClient(app)
    r = client.get("/login")
    token = r.cookies.get("csrf_token")
    resp = client.post(
        "/login",
        data={"email": "a@b.c", "password": "pw", "csrf_token": token},
        allow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.cookies.get("sb_access_token") == "token"