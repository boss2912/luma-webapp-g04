"""
test_admin_page.py — รัน admin.js และ layout.js ตัวจริงด้วย node บน DOM จำลอง (#228)
=======================================================================
สิ่งที่ทดสอบ:
1. admin.js โหลดรายชื่อแล้ววาด 1 แถวต่อ 1 คน
2. server ตอบ 401 ส่งไปหน้า login · ตอบ 403 แสดงข้อความ ไม่แสดงตาราง
3. กดบันทึกส่งเฉพาะช่องที่แก้ พร้อม CSRF header · ไม่ได้แก้อะไรไม่ส่งคำขอ
4. server ปฏิเสธ แสดงข้อความของ server และไม่เขียนทับค่าที่ผู้ใช้พิมพ์
5. layout.js สร้างเมนู "จัดการผู้ใช้" เฉพาะตอน role เป็น admin

สถานการณ์ทั้งหมดอยู่ใน admin_harness.js
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).parent
ADMIN_JS = HERE.parent / "js" / "admin.js"
LAYOUT_JS = HERE.parent / "js" / "layout.js"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="ต้องมี node ถึงจะรัน JS ได้")


def _run(scenario: str) -> dict:
    out = subprocess.run(
        [NODE, str(HERE / "admin_harness.js"), scenario, str(ADMIN_JS), str(LAYOUT_JS)],
        # node พิมพ์ UTF-8 เสมอ — ไม่ระบุ encoding จะ decode ตาม locale (cp874) แล้วข้อความไทยพัง
        capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


# ------------------------------------------------------------------ admin.js

def test_load_draws_one_row_per_user():
    result = _run("load_lists_users")
    assert result["rowCount"] == 2
    assert result["tableShown"] is True
    assert result["secondName"] == "Boss"
    assert result["secondEmail"] == "boss@example.com"
    assert result["secondPassword"] == ""       # ช่องรหัสต้องว่างเสมอ server ไม่เคยส่งรหัสมา


def test_load_401_redirects_to_login():
    result = _run("load_401_redirects_to_login")
    assert result["redirectedTo"] == "login.html"
    assert result["rowCount"] == 0


def test_load_403_shows_error_and_keeps_table_hidden():
    result = _run("load_403_shows_error")
    assert result["redirectedTo"] == ""
    assert result["errorShown"] is True
    assert result["errorText"] != ""
    assert result["tableShown"] is False


def test_save_sends_only_the_changed_field_with_csrf():
    result = _run("save_sends_only_changed_fields")
    assert result["url"].endswith("/api/admin/users/2")
    assert result["body"] == {"displayName": "Boss2"}   # ไม่มี email ไม่มี password
    assert result["csrf"] == "t"
    assert result["statusClass"] == "admin-status admin-status--ok"
    assert result["buttonDisabled"] is False


def test_save_password_only_and_clears_the_box():
    result = _run("save_password_only")
    assert result["body"] == {"password": "new-password"}
    assert result["passwordBoxAfter"] == ""


def test_save_with_no_change_sends_no_request():
    result = _run("save_nothing_changed_sends_no_request")
    assert result["patchCount"] == 0
    assert result["statusClass"] == "admin-status admin-status--error"


def test_save_error_shows_server_message_and_keeps_typed_value():
    result = _run("save_error_shows_server_message")
    assert result["statusText"] == "taken"
    assert result["statusClass"] == "admin-status admin-status--error"
    assert result["emailBoxAfter"] == "admin@example.com"
    assert result["buttonDisabled"] is False


# ----------------------------------------------------------------- layout.js

def test_layout_adds_admin_link_for_admin():
    result = _run("layout_admin_gets_admin_link")
    assert result["linkCount"] == 1
    assert result["href"] == "admin.html"
    assert result["beforeUserSlot"] is True


def test_layout_adds_no_admin_link_for_normal_user():
    result = _run("layout_user_gets_no_admin_link")
    assert result["linkCount"] == 0
