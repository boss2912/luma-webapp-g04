"""
test_config.py — ทดสอบระบบ Application Factory และ Config Loader (Issue #46)
==========================================================================
สิ่งที่ทดสอบ:
1. ฟังก์ชัน create_app() สามารถสร้าง Flask App พร้อมค่าเริ่มต้นที่ถูกต้อง
2. การส่ง config_overrides สามารถแทนที่ค่าคอนฟิกได้ (จำเป็นสำหรับการทดสอบ)
"""

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app


def test_app_factory_default_config():
    """[กรณีทดสอบ]: create_app() สร้าง instance พร้อม config พื้นฐานครบถ้วน"""
    app = create_app()
    assert app is not None
    assert "SQLALCHEMY_DATABASE_URI" in app.config
    assert "SECRET_KEY" in app.config
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False


def test_app_factory_config_overrides():
    """[กรณีทดสอบ]: create_app(config_overrides) สามารถ override ค่าสำหรับ testing ได้"""
    test_overrides = {
        "TESTING": True,
        "SECRET_KEY": "custom-test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    }
    app = create_app(config_overrides=test_overrides)
    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "custom-test-secret"
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


# ==============================================================================
# ตัวรันสำหรับสั่งรันไฟล์นี้โดยตรง (Direct Runner)
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔍 กำลังทดสอบไฟล์: test_config.py (Issue #46 create_app & Config)")
    print("=" * 60)

    tests = [
        ("ตรวจสอบค่า Default Config ของ create_app()", test_app_factory_default_config),
        ("ตรวจสอบระบบ Config Overrides สำหรับ Testing", test_app_factory_config_overrides),
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
