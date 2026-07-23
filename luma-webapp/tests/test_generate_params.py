"""
tests/test_generate_params.py — Issue #5: extended generate parameters + validation
"""

from tests.conftest import register_and_login


def test_prompt_required(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={})
    assert resp.status_code == 400


def test_non_string_prompt_rejected_not_500(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": 12345})
    assert resp.status_code == 400


def test_default_params_used_when_omitted(client, mock_forge_success):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": "a cat"})
    assert resp.status_code == 200
    sent = mock_forge_success.call_args.kwargs["json"]
    assert sent["steps"] == 20
    assert sent["cfg_scale"] == 7
    assert sent["width"] == 512
    assert sent["height"] == 512
    assert sent["negative_prompt"] == ""


def test_extended_params_forwarded_to_forge(client, mock_forge_success):
    register_and_login(client)
    resp = client.post("/api/generate", json={
        "prompt": "a cat",
        "negative_prompt": "blurry, low quality",
        "steps": 35,
        "cfg_scale": 9.5,
        "width": 1024,
        "height": 768,
    })
    assert resp.status_code == 200
    sent = mock_forge_success.call_args.kwargs["json"]
    assert sent["negative_prompt"] == "blurry, low quality"
    assert sent["steps"] == 35
    assert sent["cfg_scale"] == 9.5
    assert sent["width"] == 1024
    assert sent["height"] == 768


def test_steps_over_max_rejected(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": "a cat", "steps": 999})
    assert resp.status_code == 400


def test_steps_must_be_integer(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": "a cat", "steps": "twenty"})
    assert resp.status_code == 400


def test_cfg_scale_out_of_range_rejected(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": "a cat", "cfg_scale": 500})
    assert resp.status_code == 400


def test_width_must_be_an_allowed_value(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": "a cat", "width": 999})
    assert resp.status_code == 400


def test_height_must_be_an_allowed_value(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": "a cat", "height": 100})
    assert resp.status_code == 400
