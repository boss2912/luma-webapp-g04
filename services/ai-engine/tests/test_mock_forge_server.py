"""mock Forge ต้องรับ payload รูปแบบเดียวกับที่ ai-engine ส่งจริง (issue #156)

ai-engine ส่ง init_images เป็น list ตามสเปกของ AUTOMATIC1111
(ดู test_img2img_bridge.py::test_text_mode_uses_forge_init_images_and_forwards_strength)
แต่ mock เดิมรับแค่ init_image เป็น string จึงตอบ 400 ทุกครั้ง
-> ai-engine แปลงเป็น 502 -> ผู้ใช้เห็น "AI engine ตอบกลับด้วยสถานะ 502"

เทสในไฟล์นี้เรียก handler ของ mock ตรงๆ ไม่ต้องเปิดเซิร์ฟเวอร์
"""

import base64
import importlib.util
import sys
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

TOOLS = Path(__file__).resolve().parents[3] / "tools" / "mock_forge_server.py"


def _load_mock():
    spec = importlib.util.spec_from_file_location("mock_forge_server_for_test", TOOLS)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mock_forge = _load_mock()


def _png_b64(width=8, height=8):
    output = BytesIO()
    Image.new("RGB", (width, height), "orange").save(output, format="PNG")
    return base64.b64encode(output.getvalue()).decode("ascii")


IMAGE = _png_b64()


def _body(**extra):
    base = {
        "prompt": "a cat",
        "negative_prompt": "",
        "denoising_strength": 0.7,
        "steps": 20,
        "cfg_scale": 8.0,
        "sampler_name": "Euler a",
        "seed": -1,
        "width": 512,
        "height": 512,
    }
    base.update(extra)
    return base


def test_img2img_accepts_init_images_list_like_real_forge():
    """รูปแบบที่ ai-engine ส่งจริง — เคยตอบ 400 (issue #156)"""
    status, payload = mock_forge.handle_img2img(_body(init_images=[IMAGE]))
    assert status == 200
    assert payload["images"]


def test_img2img_still_accepts_init_image_string():
    """รูปแบบเดิมของ mock — ต้องไม่พังตามไปด้วย"""
    status, payload = mock_forge.handle_img2img(_body(init_image=IMAGE))
    assert status == 200
    assert payload["images"]


def test_img2img_rejects_request_without_any_image():
    status, payload = mock_forge.handle_img2img(_body())
    assert status == 400
    assert "init_image" in payload["error"]


def test_img2img_rejects_empty_init_images_list():
    status, payload = mock_forge.handle_img2img(_body(init_images=[]))
    assert status == 400


@pytest.mark.parametrize("mode", ["inpaint", "inpaint-sketch"])
def test_inpaint_still_requires_a_mask(mode):
    status, payload = mock_forge.handle_img2img(_body(init_images=[IMAGE], mode=mode))
    assert status == 400
    assert "mask" in payload["error"]


@pytest.mark.parametrize("mode", ["inpaint", "inpaint-sketch"])
def test_inpaint_with_mask_passes(mode):
    status, payload = mock_forge.handle_img2img(_body(init_images=[IMAGE], mode=mode, mask=IMAGE))
    assert status == 200
    assert payload["mode"] == mode
