"""
test_auth.py — ทดสอบระบบ Authentication (Register, Login, Session, Logout) (Issue #50)
==================================================================================
สิ่งที่ทดสอบ:
1. การเข้าสู่ระบบสำเร็จ สร้าง Session และคืนค่า User
2. การตรวจสอบสถานะ /api/auth/me เมื่อล็อกอินและยังไม่ได้ล็อกอิน
3. การออกจากระบบ /api/auth/logout ล้าง Session
"""

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app


def test_auth_full_flow():
    """[กรณีทดสอบ]: ลำดับการทำงาน Register -> Login -> Me -> Logout"""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()

    # 1. ยังไม่ได้ล็อกอิน เรียก /me ต้องได้ 401
    res_me_before = client.get("/api/auth/me")
    assert res_me_before.status_code == 401

    # 2. เข้าสู่ระบบ
    res_login = client.post("/api/auth/login", json={
        "email": "test@luma.ai",
        "password": "password123",
    })
    assert res_login.status_code == 200
    assert res_login.get_json()["status"] == "success"

    # 3. ล็อกอินแล้ว เรียก /me ต้องได้ข้อมูลผู้ใช้
    res_me_after = client.get("/api/auth/me")
    assert res_me_after.status_code == 200
    assert res_me_after.get_json()["email"] == "test@luma.ai"

    # 4. ออกจากระบบ
    res_logout = client.post("/api/auth/logout")
    assert res_logout.status_code == 200

    # 5. หลัง logout เรียก /me ต้องได้ 401
    res_me_final = client.get("/api/auth/me")
    assert res_me_final.status_code == 401


# ==============================================================================
# ตัวรันสำหรับสั่งรันไฟล์นี้โดยตรง (Direct Runner)
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔍 กำลังทดสอบไฟล์: test_auth.py (Issue #50 Authentication & Session)")
    print("=" * 60)

    tests = [
        ("ตรวจสอบ Flow สมบูรณ์ (Register -> Login -> Me -> Logout)", test_auth_full_flow),
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
