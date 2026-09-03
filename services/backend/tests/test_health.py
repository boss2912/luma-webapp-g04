"""
test_health.py — ทดสอบการทำงานพื้นฐานและการเชื่อมต่อเซิร์ฟเวอร์
=============================================================
รันเดี่ยวๆ ได้ด้วย:
    python services/backend/tests/test_health.py
"""

import sys
import os

# ตั้งค่า path ให้เรียกใช้งาน app ได้
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def test_server_health_check(client):
    """
    [กรณีทดสอบ]: ตรวจสอบว่าเซิร์ฟเวอร์ Flask Backend ทำงานปกติหรือไม่
    """
    response = client.get("/health")
    assert response.status_code == 200, f"คาดหวัง 200 แต่ได้ {response.status_code}"
    data = response.get_json()
    assert data["status"] == "ok", "ค่า status ต้องเป็น 'ok'"
    assert data["service"] == "luma-backend", "service ต้องระบุเป็น 'luma-backend'"


# ==============================================================================
# ตัวรันสำหรับสั่งรันไฟล์นี้โดยตรง (Direct Runner)
# ==============================================================================
if __name__ == "__main__":
    from app import create_app

    print("\n" + "=" * 50)
    print("🔍 กำลังทดสอบไฟล์: test_health.py (สถานะเซิร์ฟเวอร์)")
    print("=" * 50)

    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()

    tests = [
        ("ตรวจสอบสถานะเซิร์ฟเวอร์ (GET /health)", lambda: test_server_health_check(client)),
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

    print("-" * 50)
    print(f"📊 ผลรวม: ผ่าน {passed}/{len(tests)} การทดสอบ")
    print("=" * 50 + "\n")
