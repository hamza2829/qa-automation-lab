import pytest


def test_req02_login_success(api, factory):
    r = api.login(**factory.user())
    assert r.status_code == 200 and len(r.json()["token"]) == 32


@pytest.mark.parametrize("password", ["wrong", "", "SECRET123"])
def test_req02_login_wrong_password_rejected(api, password):
    assert api.login("alice", password).status_code == 401


def test_req02_unknown_user_rejected(api):
    assert api.login("mallory", "secret123").status_code == 401


def test_req02_cart_requires_login(api):
    assert api.get("/api/cart").status_code == 401
