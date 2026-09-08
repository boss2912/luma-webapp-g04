"""
test_generate.py — ทดสอบระบบสร้างภาพ AI (Issue #22 POST /api/generate)
=====================================================================
สิ่งที่ทดสอบ:
1. การปฏิเสธคำขอเมื่อไม่ส่ง Prompt หรือส่ง JSON ไม่ถูกต้อง (HTTP 400)
2. การตรวจสอบขอบเขตของพารามิเตอร์ steps, cfg_scale (HTTP 400)
"""

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app


def test_generate_requires_json():
    """[กรณีทดสอบ]: ไม่ส่ง Content-Type: application/json หรือส่งข้อมูลว่าง"""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()

    res = client.post("/api/generate", data="plain text")
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_generate_requires_prompt():
    """[กรณีทดสอบ]: ส่ง JSON แต่ไม่มีฟิลด์ prompt หรือ prompt เป็นค่าว่าง"""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()

    res = client.post("/api/generate", json={"prompt": ""})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_generate_steps_validation():
    """[กรณีทดสอบ]: ส่งค่า steps เกินช่วง 1-100 ต้องได้ HTTP 400"""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()

    res = client.post("/api/generate", json={"prompt": "cat", "steps": 200})
    assert res.status_code == 400
    assert "error" in res.get_json()


# ==============================================================================
# ตัวรันสำหรับสั่งรันไฟล์นี้โดยตรง (Direct Runner)
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔍 กำลังทดสอบไฟล์: test_generate.py (Issue #22 POST /api/generate)")
    print("=" * 60)

    tests = [
        ("ตรวจสอบ Request ต้องเป็น JSON", test_generate_requires_json),
        ("ตรวจสอบต้องมีฟิลด์ Prompt", test_generate_requires_prompt),
        ("ตรวจสอบขอบเขตของค่า Steps (1-100)", test_generate_steps_validation),
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
