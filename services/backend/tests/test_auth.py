"""
test_auth.py — ทดสอบระบบสมาชิก (Authentication Flow)
===================================================
รันเดี่ยวๆ ได้ด้วย:
    python services/backend/tests/test_auth.py
"""

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def test_register_with_valid_data(client):
    """[กรณีทดสอบ]: สมัครสมาชิกด้วยข้อมูลที่ถูกต้องครบถ้วน"""
    payload = {
        "email": "artist@luma.ai",
        "displayName": "PixelMaster",
        "password": "strongPassword123",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200, f"คาดหวัง 200 แต่ได้ {response.status_code}"
    data = response.get_json()
    assert data.get("status") == "success", "status ต้องเป็น 'success'"
    assert data.get("user", {}).get("email") == "artist@luma.ai", "email ที่ตอบกลับไม่ตรงกับที่ส่ง"


def test_register_password_too_short(client):
    """[กรณีทดสอบ]: สมัครสมาชิกด้วยรหัสผ่านสั้นกว่า 8 ตัวอักษร"""
    payload = {
        "email": "short@luma.ai",
        "password": "1234",  # สั้นเกินไป
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400, f"รหัสผ่านสั้นควรตอบ 400 แต่ได้ {response.status_code}"
    data = response.get_json()
    assert "error" in data, "ต้องมีฟิลด์ 'error' ตอบกลับมาเพื่อแจ้งเตือนผู้ใช้"


def test_login_success_and_check_me(client):
    """[กรณีทดสอบ]: เข้าสู่ระบบสำเร็จ แล้วตรวจสอบ Session ผ่าน /api/auth/me"""
    login_res = client.post("/api/auth/login", json={
        "email": "member@luma.ai",
        "password": "password123",
    })
    assert login_res.status_code == 200, f"Login ไม่สำเร็จ คาดหวัง 200 แต่ได้ {login_res.status_code}"

    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200, f"/api/auth/me คาดหวัง 200 แต่ได้ {me_res.status_code}"
    assert me_res.get_json().get("email") == "member@luma.ai", "Session จำ email ผู้ใช้ไม่ตรง"


def test_logout_clears_session(client):
    """[กรณีทดสอบ]: ออกจากระบบแล้วต้องล้าง Session ทันที (เข้าดู /api/auth/me ซ้ำต้อง 401)"""
    client.post("/api/auth/login", json={
        "email": "logout_user@luma.ai",
        "password": "password123",
    })

    logout_res = client.post("/api/auth/logout")
    assert logout_res.status_code == 200, "Logout ต้องสำเร็จ (200)"

    me_after = client.get("/api/auth/me")
    assert me_after.status_code == 401, f"หลัง Logout ต้องเป็น 401 (Unauthorized) แต่ได้ {me_after.status_code}"


# ==============================================================================
# ตัวรันสำหรับสั่งรันไฟล์นี้โดยตรง (Direct Runner)
# ==============================================================================
if __name__ == "__main__":
    from app import create_app

    print("\n" + "=" * 60)
    print("🔍 กำลังทดสอบไฟล์: test_auth.py (ระบบสมาชิก Authentication)")
    print("=" * 60)

    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()

    tests = [
        ("สมัครสมาชิกด้วยข้อมูลถูกต้อง (POST /api/auth/register)", lambda: test_register_with_valid_data(client)),
        ("ปฏิเสธรหัสผ่านสั้นกว่า 8 ตัว (Password validation)", lambda: test_register_password_too_short(client)),
        ("เข้าสู่ระบบและจำ Session ได้ (Login & /api/auth/me)", lambda: test_login_success_and_check_me(client)),
        ("ออกจากระบบและล้าง Session (Logout flow)", lambda: test_logout_clears_session(client)),
    ]

    passed = 0
    for idx, (title, fn) in enumerate(tests, 1):
        print(f"[{idx}] {title} ...", end=" ")
        try:
            fn()
            print("✅ สำเร็จ (PASSED)")
            passed += 1
        except AssertionError as e:
            print(f"❌ ไม่ผ่าน (FAILED): {e}")
        except Exception as e:
            print(f"💥 เกิดข้อผิดพลาด (ERROR): {e}")

    print("-" * 60)
    print(f"📊 ผลรวม: ผ่าน {passed}/{len(tests)} การทดสอบ")
    print("=" * 60 + "\n")
