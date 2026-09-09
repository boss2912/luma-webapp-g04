"""
test_security.py — ทดสอบระบบความปลอดภัยตามมาตรฐาน OWASP และ Rate Limiting (Issue #51)
=====================================================================================
สิ่งที่ทดสอบ:
1. การแนบ Security Headers สำคัญในทุก Response (X-Content-Type-Options, X-Frame-Options, CSP, etc.)
2. การตั้งค่า Cookie Hardening (HttpOnly=True, SameSite=Lax)
3. ระบบ Rate Limiting ป้องกันเดารหัสผ่าน บล็อกหลังจากพยายามผิดพลาด 5 ครั้ง (HTTP 429)
"""

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app
from app.routes.auth import reset_rate_limit


def test_security_headers_present():
    """[กรณีทดสอบ]: ทุก Response ต้องแนบ Security Headers ป้องกันการโจมตีตามมาตรฐาน OWASP"""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()

    res = client.get("/health")
    assert res.status_code == 200

    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert "strict-origin-when-cross-origin" in res.headers.get("Referrer-Policy", "")
    assert "default-src" in res.headers.get("Content-Security-Policy", "")
    assert res.headers.get("Permissions-Policy") is not None


def test_cookie_security_config():
    """[กรณีทดสอบ]: Cookie Session ต้องเปิด HttpOnly=True และ SameSite=Lax"""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_login_rate_limiting():
    """[กรณีทดสอบ]: พยายาม Login ผิดพลาดติดต่อกันเกิน 5 ครั้ง ต้องถูกบล็อกด้วย HTTP 429"""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()

    test_ip = "192.168.1.99"
    reset_rate_limit(test_ip)

    # ลองผิด 5 ครั้งแรก (ต้องได้ 401 Unauthorized)
    for i in range(5):
        res = client.post(
            "/api/auth/login",
            json={"email": "victim@luma.ai", "password": "wrong-password"},  # no-secret-check
            environ_base={"REMOTE_ADDR": test_ip},
        )
        assert res.status_code == 401, f"ครั้งที่ {i+1} ต้องได้ 401"

    # ครั้งที่ 6 ต้องถูกบล็อกด้วย 429 Too Many Requests
    res_blocked = client.post(
        "/api/auth/login",
        json={"email": "victim@luma.ai", "password": "wrong-password"},  # no-secret-check
        environ_base={"REMOTE_ADDR": test_ip},
    )
    assert res_blocked.status_code == 429, f"ครั้งที่ 6 ต้องถูกบล็อกด้วย 429 แต่ได้ {res_blocked.status_code}"


# ==============================================================================
# ตัวรันสำหรับสั่งรันไฟล์นี้โดยตรง (Direct Runner)
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔍 กำลังทดสอบไฟล์: test_security.py (Issue #51 OWASP & Rate Limit)")
    print("=" * 60)

    tests = [
        ("ตรวจสอบ Security Headers ใน Response", test_security_headers_present),
        ("ตรวจสอบการตั้งค่า Cookie Hardening", test_cookie_security_config),
        ("ตรวจสอบ Rate Limiting บล็อกหลังลองผิด 5 ครั้ง (HTTP 429)", test_login_rate_limiting),
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
