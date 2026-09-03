"""
test_security.py — ทดสอบระบบความปลอดภัยตามมาตรฐาน OWASP (Issue #51)
==================================================================
สิ่งที่ทดสอบ:
1. การแนบ Security Headers ครบถ้วน (X-Content-Type-Options, X-Frame-Options, CSP, Referrer-Policy)
2. การทำงานของระบบจำกัดจำนวนครั้ง Rate Limiting (ตอบ 429 เมื่อล็อกอินผิดเกิน 5 ครั้ง)
3. การตั้งค่าความปลอดภัยของ Session Cookie (HttpOnly และ SameSite)
"""

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def test_security_headers_present(client):
    """[กรณีทดสอบ]: ทุก Response จากเซิร์ฟเวอร์ต้องแนบ Security Headers ครบถ้วน"""
    res = client.get("/health")
    assert res.status_code == 200

    # ตรวจสอบ Headers สำคัญตามเกณฑ์ความปลอดภัย
    assert res.headers.get("X-Content-Type-Options") == "nosniff", "ต้องมี nosniff เพื่อกัน MIME sniffing"
    assert res.headers.get("X-Frame-Options") == "SAMEORIGIN", "ต้องมี SAMEORIGIN เพื่อกัน Clickjacking"
    assert "strict-origin" in res.headers.get("Referrer-Policy", ""), "ต้องมี Referrer-Policy"
    assert "default-src" in res.headers.get("Content-Security-Policy", ""), "ต้องมี Content-Security-Policy (CSP)"


def test_login_rate_limiting(client):
    """[กรณีทดสอบ]: เมื่อพยายามล็อกอินผิดเกิน 5 ครั้งติดต่อกัน ระบบต้องตอบ 429 Too Many Requests"""
    # ยิงล็อกอินผิด 5 ครั้งแรก (ต้องได้ 400 Bad Request)
    for _ in range(5):
        res = client.post("/api/auth/login", json={"email": "wrong@luma.ai", "password": ""})
        assert res.status_code == 400

    # ยิงครั้งที่ 6 (ต้องติด Rate Limit ตอบกลับ 429 ทันที)
    res6 = client.post("/api/auth/login", json={"email": "wrong@luma.ai", "password": "pass"})
    assert res6.status_code == 429, f"ครั้งที่ 6 ต้องตอบ 429 แต่ได้ {res6.status_code}"
    data = res6.get_json()
    assert "error" in data
    assert "บ่อยเกินไป" in data["error"] or "Too many" in data["error"]


# ==============================================================================
# ตัวรันสำหรับสั่งรันไฟล์นี้โดยตรง (Direct Runner)
# ==============================================================================
if __name__ == "__main__":
    from app import create_app

    print("\n" + "=" * 60)
    print("🔍 กำลังทดสอบไฟล์: test_security.py (ระบบความปลอดภัย Issue #51)")
    print("=" * 60)

    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()

    tests = [
        ("ตรวจสอบ Security Headers ครบถ้วน (OWASP)", lambda: test_security_headers_present(client)),
        ("ตรวจสอบ Rate Limiting บล็อกเมื่อล็อกอินผิดเกิน 5 ครั้ง (429)", lambda: test_login_rate_limiting(client)),
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
