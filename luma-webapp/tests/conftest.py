"""
tests/conftest.py — fixtures ที่ทุก test ไฟล์ใช้ร่วมกัน
--------------------------------------------------------
รวมจาก 2 branch ที่แยกกันตาม issue (feature/backend-auth-issue2-3 Issue #2/#3 และ
feature/forge-ai-issue5-6 Issue #5/#6) — ทั้งสองฝั่งเขียน fixture ชุดเดียวกันไว้
โดยตั้งใจ ตอน merge จึงใช้ superset ตามที่คอมเมนต์ในทั้งสองไฟล์ระบุไว้

  app     : Flask app instance ที่ config ใหม่สำหรับ test โดยเฉพาะ (in-memory
            SQLite, ปิด CSRF, ไม่ต้องมี instance/config.py ในเครื่อง)
  client  : Flask test client — เรียก route ได้เหมือน HTTP request จริงแต่ไม่ต้องรัน server
  mock_forge_success : patch requests.post ให้ตอบเหมือน Forge AI ส่ง PNG กลับมาสำเร็จ
"""

import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# ให้ `from app import ...` ทำงานได้แม้รัน pytest จาก repo root ไม่ใช่จาก luma-webapp/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db  # noqa: E402  (ต้องมาหลัง sys.path.insert)

# 1x1 red PNG — เหมือนตัวที่ใช้ตอนทดสอบ manual ด้วย mock server
TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


@pytest.fixture()
def app():
    test_app = create_app(config_overrides={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key-not-for-real-use",
        "WTF_CSRF_ENABLED": False,  # ปิดเฉพาะตอน test — CSRFProtect ยังทำงานจริงตอน run.py
    })
    yield test_app
    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def mock_forge_success():
    """จำลอง Forge AI ตอบกลับสำเร็จพร้อมรูป 1x1 PNG — ไม่ต้องมี Stable Diffusion WebUI จริง"""
    with patch("app.routes.api.requests.post") as mock_post:
        response = MagicMock()
        response.json.return_value = {"images": [TINY_PNG_B64]}
        mock_post.return_value = response  # .raise_for_status() no-ops on a bare MagicMock
        yield mock_post


def register(client, username="tester1", email="tester1@example.com", password="password123"):
    return client.post("/auth/register", data={
        "username": username, "email": email, "password": password,
    }, follow_redirects=True)


def login(client, email="tester1@example.com", password="password123"):
    return client.post("/auth/login", data={
        "email": email, "password": password,
    })


def register_and_login(client, username="tester1", email="tester1@example.com", password="password123"):
    register(client, username, email, password)
    return login(client, email, password)
