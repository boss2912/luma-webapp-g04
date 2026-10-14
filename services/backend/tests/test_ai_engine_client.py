"""
test_ai_engine_client.py — backend แนบ X-LUMA-Engine-Key ตอนเรียก /pipeline/* (#210)
=====================================================================================
forge_client.py (เส้นทาง generate) มีเทสแนบ key อยู่แล้ว แต่ ai_engine_client.py
(เส้นทาง /api/pipeline/* — remove-background, blur, palette, ฯลฯ ที่เกี่ยวกับ #220
ตรงๆ) ยังไม่มีเทสยืนยันว่าแนบ header จริง
"""

import sys
import os
from unittest.mock import Mock, patch

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from app.services.ai_engine_client import extract_color_palette


def test_post_pipeline_passes_ai_engine_key_header():
    """[Issue #210]: เมื่อตั้งค่า AI_ENGINE_KEY ไว้ ทุกคำขอ /pipeline/* ต้องแนบ header X-LUMA-Engine-Key"""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "AI_ENGINE_URL": "http://ai-host:8000",
        "AI_ENGINE_KEY": "secret-token-xyz",
    })
    ai_engine_reply = Mock(status_code=200)
    ai_engine_reply.json.return_value = {"metrics": {"color_palette": ["#2f3ba3"]}}

    with app.app_context(), \
            patch("app.services.ai_engine_client.requests.post", return_value=ai_engine_reply) as post:
        extract_color_palette("aGk=")

    headers = post.call_args.kwargs.get("headers", {})
    assert headers.get("X-LUMA-Engine-Key") == "secret-token-xyz"


def test_post_pipeline_omits_header_when_key_not_configured():
    """[Issue #210]: ถ้าไม่ได้ตั้ง AI_ENGINE_KEY ต้องไม่ส่ง header เปล่าๆ ไปเลย (dev เครื่องเดียว)"""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "AI_ENGINE_URL": "http://ai-host:8000",
    })
    ai_engine_reply = Mock(status_code=200)
    ai_engine_reply.json.return_value = {"metrics": {"color_palette": ["#2f3ba3"]}}

    with app.app_context(), \
            patch("app.services.ai_engine_client.requests.post", return_value=ai_engine_reply) as post:
        extract_color_palette("aGk=")

    headers = post.call_args.kwargs.get("headers", {})
    assert "X-LUMA-Engine-Key" not in headers
