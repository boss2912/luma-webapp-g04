"""
tests/test_e2e_flow.py — Issue #6: full flow register -> login -> generate -> view image
"""

from tests.conftest import register, login, register_and_login


def test_full_flow_register_login_generate_view_image(client, mock_forge_success):
    # 1) register
    resp = register(client)
    assert resp.status_code == 200  # followed the redirect to the login page

    # 2) login
    resp = login(client)
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/dashboard"

    # 3) generate
    resp = client.post("/api/generate", json={"prompt": "a cat wizard, digital art"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "success"
    assert "asset_id" in body
    assert body["image_url"] == f"/api/assets/{body['asset_id']}/image"
    mock_forge_success.assert_called_once()

    # 4) view the generated image
    resp = client.get(body["image_url"])
    assert resp.status_code == 200
    assert resp.content_type == "image/png"

    # gallery reflects the new asset with its prompt
    resp = client.get("/api/assets")
    assert resp.status_code == 200
    assets = resp.get_json()
    assert len(assets) == 1
    assert assets[0]["prompt"] == "a cat wizard, digital art"


def test_dashboard_requires_login(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]


def test_dashboard_reachable_after_login(client):
    register_and_login(client)
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"tester1" in resp.data
