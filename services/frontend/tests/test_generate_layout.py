"""
test_generate_layout.py — ตำแหน่งป้ายสถานะในหน้าสร้างภาพ
==========================================================
ป้าย "AI กำลังสร้างภาพ…" ต้องอยู่เหนือกรอบภาพ ไม่ใช่อยู่ใน .preview-container
"""

from pathlib import Path

PAGE = Path(__file__).parent.parent / "pages" / "generate.html"


def test_status_label_is_above_the_preview_frame_not_inside_it():
    """[กรณีทดสอบ]: ป้ายสถานะต้องมาก่อน .preview-container ในหน้า

    .preview-container เป็น flex — ถ้าป้ายอยู่ข้างใน พอมีภาพเก่าเต็มกรอบแล้วกดสร้างรอบที่ 2
    ป้ายจะถูกบีบเป็นแถบแคบๆ ชิดขอบขวาของภาพจนอ่านไม่ออก
    """
    html = PAGE.read_text(encoding="utf-8")
    status_at = html.index('id="generate-spinner"')
    frame_at = html.index('id="preview-container"')
    assert status_at < frame_at
