"""
test_generate.py — ทดสอบระบบสร้างภาพ AI และการตรวจสอบข้อมูล
===========================================================
รันเดี่ยวๆ ได้ด้วย:
    python services/backend/tests/test_generate.py
"""

import sys
import os
from unittest.mock import patch

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.models import Asset


def test_generate_requires_prompt(client):
    """[กรณีทดสอบ]: สั่งสร้างภาพโดยไม่ระบุ Prompt หรือส่งเป็นค่าว่าง"""
    payload = {"prompt": "   "}
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 400, f"Prompt ว่างต้องตอบ 400 แต่ได้ {response.status_code}"
    data = response.get_json()
    assert "error" in data, "ต้องมีฟิลด์ error แจ้งเตือนผู้ใช้"


def test_generate_rejects_out_of_bounds_steps(client):
    """[กรณีทดสอบ]: ส่งค่า Steps เกินกว่าที่ระบบกำหนด (เกิน 100)"""
    payload = {
        "prompt": "beautiful sunrise",
        "steps": 999,
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 400, f"Steps เกิน 100 ต้องตอบ 400 แต่ได้ {response.status_code}"


def test_generate_rejects_out_of_bounds_cfg_scale(client):
    """[กรณีทดสอบ]: ส่งค่า CFG Scale เกิน 30"""
    payload = {
        "prompt": "beautiful sunrise",
        "cfg_scale": 50.0,
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 400, f"CFG Scale เกิน 30 ต้องตอบ 400 แต่ได้ {response.status_code}"


@patch("app.routes.api.generate_image")
def test_generate_success_saves_to_database(mock_generate, client, app):
    """[กรณีทดสอบ]: สั่งสร้างภาพสำเร็จ และตรวจสอบการบันทึกลง Database"""
    mock_generate.return_value = ("uploads/generated/2026/09/sample.png", 54321)

    payload = {
        "prompt": "1girl, cute cat, anime style",
        "steps": 20,
        "cfg_scale": 8.0,
        "sampler_name": "DPM++ 2M Karras",
        "seed": 54321,
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200, f"สร้างภาพต้องได้ 200 แต่ได้ {response.status_code}"
    data = response.get_json()
    assert data.get("status") == "success", "status ต้องเป็น 'success'"
    assert "asset_id" in data, "ต้องมี asset_id ตอบกลับมา"

    with app.app_context():
        asset = Asset.query.get(data["asset_id"])
        assert asset is not None, "ไม่พบข้อมูล Asset ใน Database"
        assert asset.prompt == "1girl, cute cat, anime style", "ข้อความ Prompt ใน Database ไม่ตรง"


# ==============================================================================
# ตัวรันสำหรับสั่งรันไฟล์นี้โดยตรง (Direct Runner)
# ==============================================================================
if __name__ == "__main__":
    from app import create_app
    from app.models import db

    print("\n" + "=" * 60)
    print("🔍 กำลังทดสอบไฟล์: test_generate.py (ระบบสร้างภาพ AI)")
    print("=" * 60)

    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()

    with app.app_context():
        db.create_all()

    tests = [
        ("ตรวจสอบเงื่อนไข Prompt ต้องไม่ว่าง", lambda: test_generate_requires_prompt(client)),
        ("ตรวจสอบ Steps ต้องไม่เกินขอบเขต", lambda: test_generate_rejects_out_of_bounds_steps(client)),
        ("ตรวจสอบ CFG Scale ต้องไม่เกินขอบเขต", lambda: test_generate_rejects_out_of_bounds_cfg_scale(client)),
        ("สร้างภาพสำเร็จและบันทึกลงฐานข้อมูล", lambda: test_generate_success_saves_to_database(client=client, app=app)),
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
