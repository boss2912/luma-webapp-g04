"""
tests/test_assets_delete.py — Issue #3: DELETE /api/assets/<id>
"""

from tests.conftest import register, login, register_and_login


def _generate(client, prompt="delete test"):
    resp = client.post("/api/generate", json={"prompt": prompt})
    assert resp.status_code == 200
    return resp.get_json()


def test_delete_requires_login(client, mock_forge_success):
    register_and_login(client)
    asset = _generate(client)
    client.post("/auth/logout")

    resp = client.delete(f"/api/assets/{asset['asset_id']}")
    assert resp.status_code == 401


def test_delete_requires_ownership(client, mock_forge_success):
    register_and_login(client, username="owner", email="owner@example.com")
    asset = _generate(client)
    client.post("/auth/logout")

    register(client, username="intruder", email="intruder@example.com")
    login(client, email="intruder@example.com")

    resp = client.delete(f"/api/assets/{asset['asset_id']}")
    assert resp.status_code == 404

    # still there for the real owner afterward — must log out the intruder
    # first, since login() no-ops while a session is already authenticated
    client.post("/auth/logout")
    login(client, email="owner@example.com")
    resp = client.get(asset["image_url"])
    assert resp.status_code == 200


def test_delete_removes_asset_and_is_idempotent_safe(client, mock_forge_success):
    register_and_login(client)
    asset = _generate(client)

    resp = client.delete(f"/api/assets/{asset['asset_id']}")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "deleted", "asset_id": asset["asset_id"]}

    resp = client.get(asset["image_url"])
    assert resp.status_code == 404

    resp = client.get("/api/assets")
    assert resp.get_json() == []

    # deleting again must not 500
    resp = client.delete(f"/api/assets/{asset['asset_id']}")
    assert resp.status_code == 404


def test_delete_nonexistent_asset_is_404(client):
    register_and_login(client)
    resp = client.delete("/api/assets/9999")
    assert resp.status_code == 404
