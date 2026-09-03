"""
test_backend_api.py — ชุดแบบทดสอบระบบ Flask Backend API (LUMA)
==============================================================
ทดสอบการทำงานของ Endpoints ทุกตัวตามสเปก API Contract:
1. การตรวจสอบสถานะเซิร์ฟเวอร์ (/health)
2. ระบบ Authentication (/api/auth/register, login, logout, me)
3. การตรวจสอบความถูกต้องของข้อมูล (Input Validation สำหรับ /api/generate)
4. การจัดการคลังภาพและการแบ่งหน้า (/api/assets)
"""

from unittest.mock import patch
from app.models import db, Asset


# ==============================================================================
# 1. ทดสอบการตรวจสุขภาพเซิร์ฟเวอร์ (/health)
# ==============================================================================
def test_health_check(client):
    """ทดสอบว่า endpoint /health ตอบกลับสถานะ 200 พร้อม JSON ที่ถูกต้อง"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "luma-backend"


# ==============================================================================
# 2. ทดสอบระบบ Authentication (/api/auth/*)
# ==============================================================================
def test_register_success(client):
    """ทดสอบการสมัครสมาชิกสำเร็จเมื่อกรอกข้อมูลถูกต้องครบถ้วน"""
    payload = {
        "email": "test@example.com",
        "displayName": "TestUser",
        "password": "password123",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["user"]["email"] == "test@example.com"


def test_register_password_too_short(client):
    """ทดสอบว่าระบบปฏิเสธการสมัครสมาชิกถ้ารหัสผ่านสั้นกว่า 8 ตัวอักษร (ตอบกลับ 400)"""
    payload = {
        "email": "test@example.com",
        "displayName": "TestUser",
        "password": "123",  # สั้นเกินไป
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_login_and_logout_flow(client):
    """ทดสอบ Flow การเข้าสู่ระบบ ตรวจสอบสถานะ Session และออกจากระบบ"""
    # 1. เข้าสู่ระบบ
    login_payload = {
        "email": "user@example.com",
        "password": "password123",
    }
    login_res = client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    assert login_res.get_json()["status"] == "success"

    # 2. ตรวจสอบว่า Session จำผู้ใช้ได้ผ่าน /api/auth/me
    me_res = client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.get_json()["email"] == "user@example.com"

    # 3. ออกจากระบบ
    logout_res = client.post("/api/auth/logout")
    assert logout_res.status_code == 200

    # 4. ตรวจสอบว่า Session ถูกล้างแล้ว (ต้องตอบกลับ 401 Unauthorized)
    me_after_logout = client.get("/api/auth/me")
    assert me_after_logout.status_code == 401


# ==============================================================================
# 3. ทดสอบการตรวจสอบความถูกต้องของข้อมูลในการสร้างภาพ (/api/generate Validation)
# ==============================================================================
def test_generate_missing_prompt(client):
    """ทดสอบว่าถ้าไม่ใส่ prompt ระบบต้องตอบกลับ 400 Bad Request"""
    payload = {"prompt": ""}
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_generate_invalid_steps(client):
    """ทดสอบว่าถ้าส่งค่า steps ผิดประเภท (เช่น ตัวหนังสือหรือตัวเลขเกิน) ต้องตอบกลับ 400"""
    payload = {
        "prompt": "cute cat",
        "steps": 999,  # เกินขอบเขต 1-100
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 400


def test_generate_invalid_cfg_scale(client):
    """ทดสอบว่าถ้าส่งค่า cfg_scale เกินช่วง 1-30 ต้องตอบกลับ 400"""
    payload = {
        "prompt": "cute cat",
        "cfg_scale": 50.0,
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 400


# ==============================================================================
# 4. ทดสอบการสร้างภาพสำเร็จและการบันทึกลง Database
# ==============================================================================
@patch("app.routes.api.generate_image")
def test_generate_success_flow(mock_gen, client, app):
    """ทดสอบการสร้างภาพสำเร็จ โดยจำลองการทำงานของ Forge AI Client"""
    # จำลองว่า AI สร้างภาพเสร็จและคืน path ไฟล์และ seed กลับมา
    mock_gen.return_value = ("uploads/generated/2026/08/mock_image.png", 12345)

    payload = {
        "prompt": "1girl in sakura garden",
        "steps": 20,
        "cfg_scale": 8.0,
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "asset_id" in data
    assert data["image_url"] == f"/api/assets/{data['asset_id']}/image"

    # ตรวจสอบว่าข้อมูลถูกบันทึกลงใน Database จริง
    with app.app_context():
        asset = Asset.query.get(data["asset_id"])
        assert asset is not None
        assert asset.prompt == "1girl in sakura garden"


# ==============================================================================
# 5. ทดสอบการดึงรายการคลังภาพ (/api/assets) และการแบ่งหน้า (Pagination)
# ==============================================================================
def test_list_assets_pagination(client, app):
    """ทดสอบการดึงรายการภาพ และการแบ่งหน้า (Pagination) เรียงจากใหม่ไปเก่า"""
    # เพิ่มภาพตัวอย่าง 3 ภาพลง Database
    with app.app_context():
        a1 = Asset(prompt="First image", file_path="path1.png")
        a2 = Asset(prompt="Second image", file_path="path2.png")
        a3 = Asset(prompt="Third image", file_path="path3.png")
        db.session.add_all([a1, a2, a3])
        db.session.commit()

    # ดึงข้อมูลผ่าน API
    response = client.get("/api/assets?page=1&per_page=2")
    assert response.status_code == 200
    data = response.get_json()

    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["per_page"] == 2
    # ตรวจสอบว่าภาพใหม่สุด (Third image) ต้องอยู่เป็นอันดับแรก
    assert data["items"][0]["prompt"] == "Third image"


# ==============================================================================
# 6. ทดสอบการค้นหาภาพด้วยข้อความ Prompt (?q=...)
# ==============================================================================
def test_search_assets(client, app):
    """ทดสอบการค้นหาภาพในคลังผลงานด้วยข้อความใน Prompt"""
    with app.app_context():
        a1 = Asset(prompt="cyberpunk city night", file_path="p1.png")
        a2 = Asset(prompt="anime girl portrait", file_path="p2.png")
        db.session.add_all([a1, a2])
        db.session.commit()

    # ค้นหาคำว่า "cyberpunk"
    response = client.get("/api/assets?q=cyberpunk")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 1
    assert data["items"][0]["prompt"] == "cyberpunk city night"
