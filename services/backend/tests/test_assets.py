"""
test_assets.py — ทดสอบระบบคลังผลงาน (Asset Hub, Pagination, Search)
==================================================================
รันเดี่ยวๆ ได้ด้วย:
    python services/backend/tests/test_assets.py
"""

import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.models import db, Asset


def test_list_assets_ordered_by_newest(client, app):
    """[กรณีทดสอบ]: ดึงรายการภาพทั้งหมด ภาพที่สร้างล่าสุดต้องอยู่บนสุด"""
    with app.app_context():
        db.session.query(Asset).delete()
        a1 = Asset(prompt="Oldest image", file_path="p1.png")
        a2 = Asset(prompt="Middle image", file_path="p2.png")
        a3 = Asset(prompt="Newest image", file_path="p3.png")
        db.session.add_all([a1, a2, a3])
        db.session.commit()

    response = client.get("/api/assets")
    assert response.status_code == 200, f"ดึงภาพไม่สำเร็จ ได้ {response.status_code}"
    data = response.get_json()
    assert data["total"] == 3, f"จำนวนภาพต้องมี 3 แต่ได้ {data['total']}"
    assert data["items"][0]["prompt"] == "Newest image", "ภาพล่าสุดต้องอยู่เป็นอันดับแรก"


def test_assets_pagination(client, app):
    """[กรณีทดสอบ]: แบ่งหน้าแสดงผล เช่น มี 5 ภาพ ขอหน้าละ 2 ภาพ"""
    with app.app_context():
        db.session.query(Asset).delete()
        for i in range(1, 6):
            db.session.add(Asset(prompt=f"Image #{i}", file_path=f"p{i}.png"))
        db.session.commit()

    response = client.get("/api/assets?page=1&per_page=2")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 5, f"total ต้องเป็น 5 แต่ได้ {data['total']}"
    assert len(data["items"]) == 2, f"จำนวนภาพในหน้านี้ต้องมี 2 แต่ได้ {len(data['items'])}"
    assert data["page"] == 1, "เลขหน้าปัจจุบันต้องเป็น 1"


def test_search_assets_by_prompt_query(client, app):
    """[กรณีทดสอบ]: ค้นหาภาพที่มีคำว่า 'sakura' อยู่ใน Prompt"""
    with app.app_context():
        db.session.query(Asset).delete()
        a1 = Asset(prompt="1girl walking under sakura tree", file_path="sakura.png")
        a2 = Asset(prompt="robot in cyberpunk city", file_path="robot.png")
        db.session.add_all([a1, a2])
        db.session.commit()

    response = client.get("/api/assets?q=sakura")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 1, f"ค้นหา 'sakura' ควรเจอ 1 ภาพ แต่ได้ {data['total']}"
    assert data["items"][0]["prompt"] == "1girl walking under sakura tree"


# ==============================================================================
# ตัวรันสำหรับสั่งรันไฟล์นี้โดยตรง (Direct Runner)
# ==============================================================================
if __name__ == "__main__":
    from app import create_app

    print("\n" + "=" * 60)
    print("🔍 กำลังทดสอบไฟล์: test_assets.py (คลังภาพและการค้นหา)")
    print("=" * 60)

    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    client = app.test_client()

    with app.app_context():
        db.create_all()

    tests = [
        ("เรียงลำดับภาพจากใหม่สุดไปเก่าสุด", lambda: test_list_assets_ordered_by_newest(client=client, app=app)),
        ("การแบ่งหน้าแสดงผล (Pagination)", lambda: test_assets_pagination(client=client, app=app)),
        ("การค้นหาภาพด้วยคำใน Prompt (?q=...)", lambda: test_search_assets_by_prompt_query(client=client, app=app)),
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
