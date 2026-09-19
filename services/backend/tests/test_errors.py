"""
test_errors.py — ทดสอบ Blueprint และ JSON Error Handlers (Issue #47)
===================================================================
สิ่งที่ทดสอบ:
1. การทำงานของ Blueprint api (/api/ping) และ auth (/api/auth/ping)
2. เมื่อเกิด Error 404 (Not Found) ระบบต้องตอบกลับเป็น JSON ไม่ใช่หน้า HTML
3. เมื่อเกิด Error 401 (Unauthorized) ระบบต้องตอบกลับเป็น JSON พร้อมสถานะ 401
"""

import sys
import os
from flask import abort

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app


def test_blueprints_registered():
    """[กรณีทดสอบ]: Blueprint api และ auth ถูกลงทะเบียนและเข้าถึงได้"""
    app = create_app({"TESTING": True})
    client = app.test_client()

    res_api = client.get("/api/ping")
    assert res_api.status_code == 200
    assert res_api.get_json()["blueprint"] == "api"

    res_auth = client.get("/api/auth/ping")
    assert res_auth.status_code == 200
    assert res_auth.get_json()["blueprint"] == "auth"


def test_404_returns_json():
    """[กรณีทดสอบ]: เมื่อเข้า URL ที่ไม่มีอยู่ ต้องได้ HTTP 404 และ Body เป็น JSON"""
    app = create_app({"TESTING": True})
    client = app.test_client()

    res = client.get("/this-route-does-not-exist")
    assert res.status_code == 404
    assert res.is_json
    data = res.get_json()
    assert "error" in data


def test_401_returns_json():
    """[กรณีทดสอบ]: เมื่อเกิด 401 Unauthorized ต้องตอบกลับเป็น JSON"""
    app = create_app({"TESTING": True})

    # จำลอง route ที่ abort(401)
    @app.route("/test-unauthorized")
    def trigger_401():
        abort(401)

    client = app.test_client()
    res = client.get("/test-unauthorized")
    assert res.status_code == 401
    assert res.is_json
    data = res.get_json()
    assert "error" in data


# ==============================================================================
# ตัวรันสำหรับสั่งรันไฟล์นี้โดยตรง (Direct Runner)
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔍 กำลังทดสอบไฟล์: test_errors.py (Issue #47 Blueprints & Errors)")
    print("=" * 60)

    tests = [
        ("ตรวจสอบการลงทะเบียน Blueprint (/api และ /api/auth)", test_blueprints_registered),
        ("ตรวจสอบ Error Handler 404 ตอบกลับเป็น JSON", test_404_returns_json),
        ("ตรวจสอบ Error Handler 401 ตอบกลับเป็น JSON", test_401_returns_json),
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
