"""
conftest.py — Fixtures สำหรับทดสอบ Backend ด้วย pytest
"""

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pytest
from app import create_app
from app.models import db


@pytest.fixture
def app():
    """สร้าง App ชั่วคราวสำหรับการทดสอบโดยใช้ฐานข้อมูล SQLite ใน RAM (:memory:)"""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test-secret-key",
        # เทสใช้อีเมลสมมุติ (@luma.ai) — ปิดการจำกัดโดเมนตอนสมัคร
        # เทสที่ตรวจเรื่องโดเมนอยู่ใน test_auth.py
        "ALLOWED_EMAIL_DOMAINS": None,
    }
    app = create_app(config_overrides=test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test Client สำหรับยิง request จำลองเข้า Flask App"""
    return app.test_client()


def log_in_test_user(app, client):
    """ใส่ session ของผู้ใช้จริง 1 คนให้ client — สำหรับเทสต์ที่สร้าง app เองและแค่ต้องผ่านด่าน "ต้องล็อกอิน"

    ใส่แค่ sess["user_id"] ไม่พอแล้ว: auth.py เตะ session ที่ไม่มีตรา pw_stamp และเทียบตรากับ
    รหัสผ่านในตาราง users ทุกคำขอ จึงต้องมีตารางและผู้ใช้อยู่ในฐานจริง
    """
    from werkzeug.security import generate_password_hash

    from app.models import User
    from app.routes.auth import password_stamp

    with app.app_context():
        db.create_all()
        user = User(username="tester", email="tester@example.com",
                    password_hash=generate_password_hash("password123"))
        db.session.add(user)
        db.session.commit()
        user_id, stamp = user.id, password_stamp(user)
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["pw_stamp"] = stamp
