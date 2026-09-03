"""
test_logging.py — ทดสอบระบบ Logging ไม่พิมพ์ซ้ำซ้อน (Issue #48)
=============================================================
สิ่งที่ทดสอบ:
1. การเรียก create_app() ซ้ำหลายๆ ครั้ง (เช่น ตอนรัน pytest) ต้องไม่เพิ่ม Handler ซ้ำ
2. รูปแบบ Log และ Handler ของ Flask Logger ต้องมีเพียง 1 ตัวเสมอ
"""

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app


def test_logging_handlers_not_duplicated():
    """
    [กรณีทดสอบ]: เรียก create_app() หลายๆ ครั้ง Handler ของ logger ต้องไม่เบิ้ล
    [ผลลัพธ์ที่คาดหวัง]:
      - len(app.logger.handlers) == 1 เสมอ
      - app.logger.propagate == False (ไม่ส่งต่อไป root logger ซ้ำ)
    """
    app1 = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    app2 = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    app3 = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    # ตรวจสอบว่า app ตัวล่าสุดมี handler เพียง 1 ตัว ไม่บวมขึ้นเป็น 3 ตัว
    assert len(app3.logger.handlers) == 1, f"Handler ต้องมี 1 ตัว แต่พบ {len(app3.logger.handlers)}"
    assert app3.logger.propagate is False, "propagate ต้องเป็น False เพื่อไม่ให้ Log เบิ้ลไปที่ root"


# ==============================================================================
# ตัวรันสำหรับสั่งรันไฟล์นี้โดยตรง (Direct Runner)
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔍 กำลังทดสอบไฟล์: test_logging.py (ระบบ Logging ไม่ซ้อน Issue #48)")
    print("=" * 60)

    tests = [
        ("ตรวจสอบ Logger Handlers ไม่เบิ้ลซ้ำซ้อน", test_logging_handlers_not_duplicated),
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
