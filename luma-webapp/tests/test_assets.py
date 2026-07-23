"""
tests/test_assets.py — ownership / IDOR regression tests (F05)

Delete-endpoint tests (Issue #3) live in the feature/backend-auth-issue2-3
branch's own test_assets_delete.py, next to the endpoint itself — that
endpoint isn't part of this branch.
"""

from tests.conftest import register, login, register_and_login


def _generate(client, prompt="idor test"):
    resp = client.post("/api/generate", json={"prompt": prompt})
    assert resp.status_code == 200
    return resp.get_json()


def test_image_requires_login(client, mock_forge_success):
    register_and_login(client)
    asset = _generate(client)
    client.post("/auth/logout")

    resp = client.get(asset["image_url"])
    assert resp.status_code == 401


def test_image_owner_can_view(client, mock_forge_success):
    register_and_login(client)
    asset = _generate(client)
    resp = client.get(asset["image_url"])
    assert resp.status_code == 200


def test_image_non_owner_gets_404_not_someone_elses_image(client, mock_forge_success):
    register_and_login(client, username="owner", email="owner@example.com")
    asset = _generate(client)
    client.post("/auth/logout")

    register(client, username="intruder", email="intruder@example.com")
    login(client, email="intruder@example.com")

    resp = client.get(asset["image_url"])
    assert resp.status_code == 404
