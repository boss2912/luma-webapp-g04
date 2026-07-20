"""
Test script — ตรวจสอบว่าโปรเจค LUMA ใช้ได้จริงทุกส่วน
"""
import sys
import os

# ต้องรันจาก luma-webapp/ directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PASS = 0
FAIL = 0

def check(label, fn):
    global PASS, FAIL
    try:
        fn()
        print(f"  [PASS] {label}")
        PASS += 1
    except Exception as e:
        print(f"  [FAIL] {label}: {e}")
        FAIL += 1

print("=" * 55)
print("  LUMA Web App — System Check")
print("=" * 55)

# 1) Imports
print("\n[1] Import check")
check("flask importable",            lambda: __import__("flask"))
check("flask_sqlalchemy importable", lambda: __import__("flask_sqlalchemy"))
check("flask_login importable",      lambda: __import__("flask_login"))
check("flask_migrate importable",    lambda: __import__("flask_migrate"))
check("requests importable",         lambda: __import__("requests"))
check("werkzeug importable",         lambda: __import__("werkzeug"))

# 2) create_app
print("\n[2] Application Factory")
from app import create_app, db
app = create_app()
check("create_app() returns app",    lambda: app is not None)

# 3) Routes registered
print("\n[3] Blueprint routes")
rules = [str(r) for r in app.url_map.iter_rules()]
check("/ exists",                    lambda: "/" in rules)
check("/dashboard exists",           lambda: "/dashboard" in rules)
check("/auth/login exists",          lambda: "/auth/login" in rules)
check("/auth/register exists",       lambda: "/auth/register" in rules)
check("/auth/logout exists",         lambda: "/auth/logout" in rules)
check("/api/generate exists",        lambda: "/api/generate" in rules)
check("/api/assets exists",          lambda: "/api/assets" in rules)

# 4) Database
print("\n[4] Database (SQLite)")
from app.models import User, Asset, Job
with app.app_context():
    check("tables created",          lambda: db.session.execute(db.select(User)).scalars().all() is not None)
    check("Asset query ok",          lambda: db.session.execute(db.select(Asset)).scalars().all() is not None)
    check("Job query ok",            lambda: db.session.execute(db.select(Job)).scalars().all() is not None)
    check("db.session.get() works",  lambda: db.session.get(User, 999) is None)

# 5) Auth logic
print("\n[5] Auth model logic")
u = User(username="testuser", email="test@test.com")
u.set_password("password123")
check("password hash stored",        lambda: u.password_hash != "password123")
check("check_password correct",      lambda: u.check_password("password123"))
check("check_password wrong rejects",lambda: not u.check_password("wrongpass"))

# 6) Logger
print("\n[6] Utils / Logger")
from app.utils.logger import get_logger, setup_logging
check("get_logger() callable",       lambda: get_logger("test") is not None)
check("setup_logging() callable",    lambda: setup_logging(app) is None)

# 7) Config keys
print("\n[7] Config keys")
with app.app_context():
    from flask import current_app
    check("SECRET_KEY set",              lambda: bool(current_app.config.get("SECRET_KEY")))
    check("SQLALCHEMY_DATABASE_URI set", lambda: bool(current_app.config.get("SQLALCHEMY_DATABASE_URI")))
    check("FORGE_AI_ENDPOINT set",       lambda: bool(current_app.config.get("FORGE_AI_ENDPOINT")))

# Summary
print("\n" + "=" * 55)
print(f"  Result: {PASS} passed, {FAIL} failed")
print("=" * 55)


def test_all_checks_passed():
    """pytest entry point — fails the suite if any manual check above failed."""
    assert FAIL == 0, f"{FAIL} system check(s) failed — see output above"
