"""
test_admin.py — ทดสอบการล็อกอินด้วยชื่อ และหน้าจัดการผู้ใช้ของ admin

สิ่งที่ทดสอบ:
1. ล็อกอินด้วยชื่อ หรืออีเมล ในช่องเดียวกันได้ทั้งคู่
2. /api/admin/* เข้าได้เฉพาะ role = admin (ไม่ล็อกอิน 401 · ผู้ใช้ทั่วไป 403)
3. admin ดูรายชื่อได้ และคำตอบไม่มีรหัสผ่านหรือ hash
4. admin แก้ชื่อ อีเมล และตั้งรหัสใหม่ได้ — รหัสใหม่ใช้ล็อกอินได้จริง
"""

import pytest
from werkzeug.security import generate_password_hash

from app.models import User, db
from app.routes.auth import _login_failed_attempts


@pytest.fixture(autouse=True)
def clear_login_attempts():
    """ล้างตัวนับการเดารหัสผิดก่อนทุก test

    ตัวนับเป็นตัวแปรระดับไฟล์ใน auth.py จึงค้างข้าม test
    ไม่ล้างแล้ว test ที่ตั้งใจล็อกอินผิดจะทำให้ test ถัดไปโดน 429 ไปด้วย
    autouse=True แปลว่า pytest เรียกให้เองทุก test ในไฟล์นี้ ไม่ต้องใส่ชื่อในวงเล็บ
    """
    _login_failed_attempts.clear()


def add_user(app, name, email, password, role="user"):
    """ใส่ผู้ใช้ลงฐานข้อมูลตรงๆ แล้วคืน id"""
    with app.app_context():
        user = User(
            username=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        return user.id


def login(client, name, password):
    return client.post("/api/auth/login", json={"login": name, "password": password})


# ---------------------------------------------------------------- login

def test_login_with_name_or_email(app, client):
    add_user(app, "Boss", "boss@example.com", "password123")

    assert login(client, "Boss", "password123").status_code == 200
    assert login(client, "boss", "password123").status_code == 200      # ไม่สนตัวพิมพ์
    assert login(client, "boss@example.com", "password123").status_code == 200
    assert login(client, "Boss", "wrong-password").status_code == 401


def test_login_still_accepts_old_email_key(app, client):
    """ของเดิมส่งคีย์ "email" มา ต้องยังล็อกอินได้"""
    add_user(app, "Boss", "boss@example.com", "password123")

    res = client.post("/api/auth/login", json={"email": "boss@example.com", "password": "password123"})
    assert res.status_code == 200


def test_name_that_looks_like_someone_elses_email_cannot_hijack_login(app, client):
    """คนที่ตั้งชื่อตัวเองเป็นอีเมลของคนอื่น ต้องไม่ถูกหยิบขึ้นมาแทนเจ้าของอีเมล"""
    add_user(app, "Victim", "victim@example.com", "victim-password")
    add_user(app, "victim@example.com", "attacker@example.com", "attacker-password")

    assert login(client, "victim@example.com", "attacker-password").status_code == 401
    assert login(client, "victim@example.com", "victim-password").status_code == 200


def test_rate_limit_counts_name_and_email_as_one_account(app, client):
    """เดาผิดด้วยชื่อ 3 ครั้ง + อีเมล 2 ครั้ง = 5 ครั้งของบัญชีเดียว -> ครั้งถัดไปโดนบล็อก"""
    add_user(app, "Boss", "boss@example.com", "password123")

    for _ in range(3):
        assert login(client, "Boss", "wrong-password").status_code == 401
    for _ in range(2):
        assert login(client, "boss@example.com", "wrong-password").status_code == 401

    assert login(client, "Boss", "password123").status_code == 429


def test_me_reports_role(app, client):
    add_user(app, "admin", "admin@example.com", "admin1234", role="admin")

    login(client, "admin", "admin1234")
    assert client.get("/api/auth/me").get_json()["role"] == "admin"


# ---------------------------------------------------------------- สิทธิ์

def test_admin_routes_need_login(client):
    assert client.get("/api/admin/users").status_code == 401
    assert client.patch("/api/admin/users/1", json={"displayName": "x"}).status_code == 401


def test_normal_user_gets_403(app, client):
    user_id = add_user(app, "Boss", "boss@example.com", "password123")
    login(client, "Boss", "password123")

    assert client.get("/api/admin/users").status_code == 403
    # แก้ข้อมูลตัวเองผ่านทาง admin ก็ไม่ได้
    res = client.patch(f"/api/admin/users/{user_id}", json={"displayName": "Hacker"})
    assert res.status_code == 403


def test_register_cannot_choose_role(app, client):
    """ส่ง role มาตอนสมัคร ต้องไม่ได้เป็น admin"""
    res = client.post("/api/auth/register", json={
        "email": "new@example.com",
        "displayName": "Newbie",
        "password": "password123",
        "role": "admin",
    })
    assert res.status_code == 201

    with app.app_context():
        assert User.query.filter_by(username="Newbie").first().role == "user"


# ---------------------------------------------------------------- ดูรายชื่อ

def test_admin_lists_users_without_password(app, client):
    add_user(app, "admin", "admin@example.com", "admin1234", role="admin")
    add_user(app, "Boss", "boss@example.com", "password123")
    login(client, "admin", "admin1234")

    res = client.get("/api/admin/users")
    assert res.status_code == 200

    items = res.get_json()["items"]
    assert [item["displayName"] for item in items] == ["admin", "Boss"]
    assert items[1] == {
        "id": items[1]["id"],
        "displayName": "Boss",
        "email": "boss@example.com",
        "role": "user",
    }
    # ทั้งคำตอบต้องไม่มีรหัสผ่านหรือ hash หลุดออกมา
    body = res.get_data(as_text=True)
    assert "password" not in body
    assert "pbkdf2" not in body and "scrypt" not in body


# ---------------------------------------------------------------- แก้ไข

def test_admin_edits_name_and_email(app, client):
    add_user(app, "admin", "admin@example.com", "admin1234", role="admin")
    user_id = add_user(app, "Boss", "boss@example.com", "password123")
    login(client, "admin", "admin1234")

    res = client.patch(f"/api/admin/users/{user_id}", json={
        "displayName": "Boss2",
        "email": "Boss2@Example.com",
    })
    assert res.status_code == 200
    assert res.get_json()["user"]["displayName"] == "Boss2"
    assert res.get_json()["user"]["email"] == "boss2@example.com"

    with app.app_context():
        user = db.session.get(User, user_id)
        assert user.username == "Boss2"
        assert user.email == "boss2@example.com"


def test_admin_sets_new_password_and_it_works(app, client):
    add_user(app, "admin", "admin@example.com", "admin1234", role="admin")
    user_id = add_user(app, "Boss", "boss@example.com", "old-password")
    login(client, "admin", "admin1234")

    res = client.patch(f"/api/admin/users/{user_id}", json={"password": "new-password"})
    assert res.status_code == 200

    client.post("/api/auth/logout")
    assert login(client, "Boss", "old-password").status_code == 401
    assert login(client, "Boss", "new-password").status_code == 200


def test_admin_edit_rejects_bad_values(app, client):
    add_user(app, "admin", "admin@example.com", "admin1234", role="admin")
    user_id = add_user(app, "Boss", "boss@example.com", "password123")
    login(client, "admin", "admin1234")
    url = f"/api/admin/users/{user_id}"

    assert client.patch(url, json={"displayName": "   "}).status_code == 400
    assert client.patch(url, json={"displayName": "x" * 81}).status_code == 400
    assert client.patch(url, json={"email": "not-an-email"}).status_code == 400
    assert client.patch(url, json={"password": "short"}).status_code == 400
    assert client.patch(url, json={"password": 12345678}).status_code == 400
    assert client.patch("/api/admin/users/999999", json={"displayName": "x"}).status_code == 404

    # ทุกคำขอข้างบนถูกปฏิเสธ ข้อมูลเดิมต้องไม่เปลี่ยน
    with app.app_context():
        user = db.session.get(User, user_id)
        assert user.username == "Boss"
        assert user.email == "boss@example.com"


def test_admin_edit_duplicate_name_is_400_and_saves_nothing(app, client):
    """ชื่อใหม่ซ้ำกับคนอื่น -> 400 และอีเมลที่ส่งมาพร้อมกันต้องไม่ถูกบันทึกครึ่งเดียว"""
    add_user(app, "admin", "admin@example.com", "admin1234", role="admin")
    user_id = add_user(app, "Boss", "boss@example.com", "password123")
    login(client, "admin", "admin1234")

    res = client.patch(f"/api/admin/users/{user_id}", json={
        "displayName": "ADMIN",
        "email": "changed@example.com",
    })
    assert res.status_code == 400

    with app.app_context():
        user = db.session.get(User, user_id)
        assert user.username == "Boss"
        assert user.email == "boss@example.com"
