"""
test_pnginfo_page.py — รัน pnginfo.js ตัวจริงด้วย node บน DOM จำลอง
=======================================================================
frontend ไม่มี build step จึงทดสอบผ่าน node (ไม่มี node ในเครื่อง -> ข้าม ไม่ถือว่าล้ม)
สถานการณ์อยู่ใน pnginfo_harness.js
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).parent
JS = HERE.parent / "js" / "pnginfo.js"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="ต้องมี node ถึงจะรัน JS ได้")


def _run(scenario: str) -> dict:
    out = subprocess.run(
        [NODE, str(HERE / "pnginfo_harness.js"), scenario, str(JS)],
        # node พิมพ์ UTF-8 เสมอ — ไม่ระบุ encoding จะ decode ตาม locale (cp874) แล้วข้อความไทยพัง
        capture_output=True, text=True, encoding="utf-8", timeout=30)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def test_submit_disabled_until_a_file_is_chosen():
    """[กรณีทดสอบ]: เปิดหน้ามาต้องกดอ่านข้อมูลไม่ได้จนกว่าจะเลือกไฟล์"""
    result = _run("start")
    assert result["submitDisabled"] is True
    assert result["resultHidden"] is True


def test_non_png_file_is_rejected_before_reading():
    """[กรณีทดสอบ]: เลือกไฟล์ที่ไม่ใช่ PNG (เช่น .jpg) -> แจ้งเตือนทันที ไม่เปิดปุ่มอ่าน"""
    result = _run("select_non_png")
    assert ".png" in result["error"]
    assert result["errorHidden"] is False
    assert result["submitDisabled"] is True
    assert result["previewHidden"] is True


def test_choosing_a_png_shows_preview_and_enables_the_button():
    result = _run("select_png")
    assert result["submitDisabled"] is False
    assert result["previewHidden"] is False
    assert result["previewSrc"].startswith("data:image/png;base64,")
    assert result["errorHidden"] is True


def test_reads_parameters_and_sends_csrf_header():
    """[กรณีทดสอบ]: กดอ่าน -> ยิง /api/pipeline/png-info พร้อม CSRF และแสดงข้อความที่ฝังไว้"""
    result = _run("read_found")
    assert result["url"].endswith("/api/pipeline/png-info")
    assert result["sentImage"].startswith("data:image/png;base64,")
    assert result["hasCsrf"] is True
    assert result["resultHidden"] is False
    assert "พบข้อมูล" in result["title"]
    assert result["parameters"] == "a fox\nSteps: 20"
    assert result["submitDisabled"] is False


def test_not_found_tells_the_user_clearly_without_a_stray_parameters_block():
    """[กรณีทดสอบ]: ไม่มี chunk ฝังอยู่ไม่ใช่ error — ต้องบอกผู้ใช้ตรงๆ ไม่ใช่โชว์กล่องว่าง"""
    result = _run("read_not_found")
    assert result["resultHidden"] is False
    assert "ไม่พบ" in result["title"]
    assert result["parameters"] == ""


def test_server_error_is_shown_and_button_recovers():
    """[กรณีทดสอบ]: server ตอบ 400 (เช่นอัปโหลดไม่ใช่ PNG จริง) -> แสดงข้อความจริง ปุ่มกลับมากดได้"""
    result = _run("read_error")
    assert "PNG" in result["error"]
    assert result["errorHidden"] is False
    assert result["resultHidden"] is True
    assert result["submitDisabled"] is False
