"""
tests/conftest.py — fixtures shared by this branch's tests (Issue #2 models, Issue #3 delete)

หมายเหตุ: ไฟล์นี้เขียนแบบเดียวกับ conftest.py ใน feature/forge-ai-issue5-6 โดยตั้งใจ
(คนละ branch ที่แยกกันตาม issue ตามที่ทีมตกลงไว้ — พอ merge เข้า develop พร้อมกันแล้ว
ไฟล์นี้จะเหลือชุดเดียว, ตอน merge conflict ให้ใช้ superset ของทั้งสองฝั่ง)
"""

import base64
from unittest.mock import patch, MagicMock

import pytest

from app import create_app, db

TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


@pytest.fixture()
def app():
    test_app = create_app(config_overrides={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key-not-for-real-use",
        "WTF_CSRF_ENABLED": False,
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
    with patch("app.routes.api.requests.post") as mock_post:
        response = MagicMock()
        response.json.return_value = {"images": [TINY_PNG_B64]}
        mock_post.return_value = response
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
