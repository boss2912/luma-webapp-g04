"""
tests/test_auth.py — regression tests for the auth fixes from the security review
(open redirect, account enumeration, password policy, rate limiting, crash-on-missing-field)
"""

from tests.conftest import register, login, register_and_login


def test_duplicate_username_and_email_rejected(client):
    register(client, username="dupe", email="dupe@example.com")
    resp = register(client, username="dupe", email="someoneelse@example.com")
    assert "ไม่สามารถ".encode() in resp.data


def test_weak_password_rejected_server_side(client):
    resp = client.post("/auth/register", data={
        "username": "weakpw", "email": "weakpw@example.com", "password": "a",
    })
    assert resp.status_code == 200  # re-renders the form with a field error, not a redirect
    assert b"8" in resp.data  # mentions the minimum length


def test_login_wrong_password_no_crash(client):
    register(client, username="u1", email="u1@example.com")
    resp = login(client, email="u1@example.com", password="wrongpassword")
    assert resp.status_code == 200


def test_login_missing_fields_does_not_500(client):
    # regression test for F03: request.form["email"] used to raise an
    # unhandled BadRequestKeyError (500) when the field was simply absent
    resp = client.post("/auth/login", data={})
    assert resp.status_code == 200


def test_open_redirect_blocked(client):
    register(client, username="u2", email="u2@example.com")
    resp = client.post(
        "/auth/login?next=https://evil.example/steal",
        data={"email": "u2@example.com", "password": "password123"},
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/dashboard"


def test_open_redirect_allows_safe_relative_path(client):
    register(client, username="u3", email="u3@example.com")
    resp = client.post(
        "/auth/login?next=/api/assets",
        data={"email": "u3@example.com", "password": "password123"},
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/api/assets"


def test_login_rate_limited_after_repeated_failures(client):
    register(client, username="u4", email="u4@example.com")
    for _ in range(5):
        login(client, email="u4@example.com", password="wrongpassword")
    resp = login(client, email="u4@example.com", password="wrongpassword")
    assert resp.status_code == 429


def test_rate_limit_does_not_block_a_different_account(client):
    register(client, username="target", email="target@example.com")
    register(client, username="bystander", email="bystander@example.com")
    for _ in range(5):
        login(client, email="target@example.com", password="wrongpassword")
    # target is now rate-limited, but an unrelated account must still work
    resp = login(client, email="bystander@example.com", password="password123")
    assert resp.status_code == 302


def test_logout_requires_post(client):
    register_and_login(client)
    resp = client.get("/auth/logout")
    assert resp.status_code == 405  # GET is no longer allowed


def test_logout_post_ends_session(client):
    register_and_login(client)
    client.post("/auth/logout")
    resp = client.get("/dashboard")
    assert resp.status_code == 302
