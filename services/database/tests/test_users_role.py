"""พิสูจน์ migration b7e2a41c9d10 — คอลัมน์ users.role และบัญชี admin ตั้งต้น

ทดสอบบนไฟล์ .db ชั่วคราวของ pytest และสร้างตารางด้วย migration จริง
ไม่ใช่ db.create_all() (ADR-008 กฎข้อ 2)
"""

import os
import sys
from pathlib import Path

import pytest
from flask_migrate import downgrade, upgrade
from sqlalchemy import inspect, text
from werkzeug.security import check_password_hash

DATABASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DATABASE_DIR))

REVISION_BEFORE = "f369fc41b5c7"
REVISION_ROLE = "b7e2a41c9d10"


@pytest.fixture()
def app(tmp_path):
    """app ที่ชี้ไฟล์ .db ชั่วคราว และหยุดที่ revision ก่อนมีคอลัมน์ role"""
    db_file = tmp_path / "test_role.db"
    os.environ["LUMA_DATABASE_URI"] = "sqlite:///" + str(db_file).replace("\\", "/")

    from migrate_app import create_migration_app

    application = create_migration_app()
    with application.app_context():
        upgrade(revision=REVISION_BEFORE)

    yield application

    os.environ.pop("LUMA_DATABASE_URI", None)


def _insert_user(db, username, email):
    db.session.execute(
        text(
            "INSERT INTO users (username, email, password_hash, created_at) "
            "VALUES (:username, :email, 'old-hash', '2026-10-01 00:00:00')"
        ),
        {"username": username, "email": email},
    )
    db.session.commit()


def _rows(db):
    """คืน {username: (role, password_hash)} ของทุกแถวใน users"""
    result = db.session.execute(text("SELECT username, role, password_hash FROM users"))
    return {row.username: (row.role, row.password_hash) for row in result}


def test_upgrade_adds_role_and_creates_admin(app):
    """ฐานเปล่า -> มีคอลัมน์ role และมีบัญชี admin ที่ล็อกอินด้วยรหัสตั้งต้นได้"""
    from app.models import db

    with app.app_context():
        upgrade(revision=REVISION_ROLE)

        columns = {c["name"] for c in inspect(db.engine).get_columns("users")}
        assert "role" in columns

        rows = _rows(db)
        assert list(rows) == ["admin"]
        role, password_hash = rows["admin"]
        assert role == "admin"
        # เก็บเป็น hash ไม่ใช่ข้อความตรงๆ และ hash นั้นตรงกับรหัสตั้งต้น
        assert password_hash != "admin1234"
        assert check_password_hash(password_hash, "admin1234")


def test_existing_users_become_role_user(app):
    """แถวที่มีอยู่ก่อน migration ต้องได้ role = user ไม่ใช่ NULL และไม่ใช่ admin"""
    from app.models import db

    with app.app_context():
        _insert_user(db, "Boss", "boss@example.com")
        upgrade(revision=REVISION_ROLE)

        rows = _rows(db)
        assert rows["Boss"] == ("user", "old-hash")
        assert rows["admin"][0] == "admin"


@pytest.mark.parametrize("username, email", [
    ("Admin", "someone@example.com"),       # ชื่อชน (NOCASE)
    ("someone", "admin@luma.local"),        # อีเมลชน
    ("admin", "admin@luma.local"),          # ชื่อและอีเมลชน แต่รหัสไม่ใช่รหัสตั้งต้น
])
def test_ordinary_account_matching_admin_is_not_promoted(app, username, email):
    """บัญชีที่ใครก็สมัครได้ ชื่อหรืออีเมลชนกับ admin -> migration หยุด ไม่ยกเป็น admin

    และต้องไม่แก้อะไรเลย: ไม่มีคอลัมน์ role, แถวเดิมไม่เปลี่ยน, revision ยังอยู่ที่เดิม
    ฐานจึงแก้ชื่อบัญชีนั้นแล้ว upgrade ใหม่ได้
    """
    from app.models import db

    with app.app_context():
        _insert_user(db, username, email)
        with pytest.raises(SystemExit):   # Flask-Migrate แปลง RuntimeError เป็น exit 1
            upgrade(revision=REVISION_ROLE)
        db.session.remove()

        columns = {c["name"] for c in inspect(db.engine).get_columns("users")}
        assert "role" not in columns
        rows = db.session.execute(text("SELECT username, email, password_hash FROM users")).all()
        assert [tuple(r) for r in rows] == [(username, email, "old-hash")]
        version = db.session.execute(text("SELECT version_num FROM alembic_version")).scalar()
        assert version == REVISION_BEFORE

        # เปลี่ยนชื่อและอีเมลแล้ว upgrade ใหม่ได้ บัญชีนั้นเป็น user ธรรมดา
        db.session.execute(text("UPDATE users SET username = 'renamed', email = 'renamed@example.com'"))
        db.session.commit()
        upgrade(revision=REVISION_ROLE)
        assert _rows(db)["renamed"] == ("user", "old-hash")
        assert _rows(db)["admin"][0] == "admin"


def test_downgrade_drops_role_and_keeps_users(app):
    """ถอยกลับ 1 ขั้น -> คอลัมน์ role หาย แต่แถวผู้ใช้ยังอยู่ครบ แล้ว upgrade ซ้ำได้"""
    from app.models import db

    with app.app_context():
        _insert_user(db, "Boss", "boss@example.com")
        upgrade(revision=REVISION_ROLE)
        downgrade(revision=REVISION_BEFORE)

        columns = {c["name"] for c in inspect(db.engine).get_columns("users")}
        assert "role" not in columns
        names = db.session.execute(text("SELECT username FROM users ORDER BY id")).scalars().all()
        assert names == ["Boss", "admin"]
        db.session.remove()

        upgrade(revision=REVISION_ROLE)
        assert _rows(db)["admin"][0] == "admin"
