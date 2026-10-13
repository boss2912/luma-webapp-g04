"""HTTP contract tests for the Function page pipeline routes (issue #163)."""

import base64
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app  # noqa: E402


def _encode_png(image):
    success, encoded = cv2.imencode(".png", image)
    assert success
    return base64.b64encode(encoded.tobytes()).decode("ascii")


def _decode_png(image_b64):
    raw = base64.b64decode(image_b64, validate=True)
    return cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)


def _checkerboard():
    image = np.zeros((24, 24, 3), dtype=np.uint8)
    for y in range(8, 16):
        for x in range(8, 16):
            image[y, x] = (255, 255, 255) if (x + y) % 2 else (0, 0, 255)
    return image


def _blur_body(**params):
    body_params = {
        "region": {"x": 8, "y": 8, "width": 8, "height": 8},
        "size": 3,
    }
    body_params.update(params)
    return {"image": _encode_png(_checkerboard()), "params": body_params}


def test_blur_route_changes_only_the_selected_region():
    original = _checkerboard()
    client = create_app({"TESTING": True}).test_client()

    response = client.post("/pipeline/02_enhancement/blur", json=_blur_body())

    assert response.status_code == 200
    assert response.json["stage"] == "02_enhancement"
    assert response.json["operation"] == "blur"
    assert set(response.json["metrics"]) == {"mean", "variance"}
    result = _decode_png(response.json["image"])
    outside = np.ones(original.shape[:2], dtype=bool)
    outside[8:16, 8:16] = False
    assert np.array_equal(result[outside], original[outside])
    assert not np.array_equal(result[8:16, 8:16], original[8:16, 8:16])


@pytest.mark.parametrize("body", [
    None,
    [],
    {"image": 123},
    {"image": "not-base64!!!"},
    {"image": base64.b64encode(b"not an image").decode("ascii")},
])
def test_blur_route_rejects_invalid_images_and_bodies(body):
    response = create_app({"TESTING": True}).test_client().post(
        "/pipeline/02_enhancement/blur", json=body
    )
    assert response.status_code == 400
    assert "error" in response.json


@pytest.mark.parametrize("params", [
    [],
    {},
    {"region": None},
    {"region": {"x": 0, "y": 0, "width": 5}},
    {"region": {"x": True, "y": 0, "width": 5, "height": 5}},
    {"region": {"x": -1, "y": 0, "width": 5, "height": 5}},
    {"region": {"x": 0, "y": 0, "width": 0, "height": 5}},
    {"region": {"x": 20, "y": 0, "width": 5, "height": 5}},
    {"region": {"x": 0, "y": 20, "width": 5, "height": 5}},
    {"region": {"x": 0, "y": 0, "width": 5, "height": 5}, "size": True},
    {"region": {"x": 0, "y": 0, "width": 5, "height": 5}, "size": 2},
    {"region": {"x": 0, "y": 0, "width": 5, "height": 5}, "size": 4},
    {"region": {"x": 0, "y": 0, "width": 5, "height": 5}, "size": 101},
])
def test_blur_route_rejects_invalid_parameters(params):
    body = {"image": _encode_png(_checkerboard()), "params": params}
    response = create_app({"TESTING": True}).test_client().post(
        "/pipeline/02_enhancement/blur", json=body
    )
    assert response.status_code == 400
    assert "error" in response.json


def _blank_image():
    return np.zeros((100, 120, 3), dtype=np.uint8)


def _contours_body(**params):
    body_params = {"confidence_min": 0.6, "min_size": 20}
    body_params.update(params)
    return {"image": _encode_png(_blank_image()), "params": body_params}


class _StubFaceDetector:
    """Same shape as cv2.FaceDetectorYN — see test_segmentation.py for the row format."""

    def __init__(self, rows):
        self._rows = None if rows is None else np.array(rows, dtype=np.float32)

    def setInputSize(self, size):
        pass

    def detect(self, image):
        return None, self._rows


def test_contours_route_returns_sorted_json_boxes_with_confidence(monkeypatch):
    rows = [
        [10, 20, 30, 40, *([0] * 10), 0.7],   # area 1200, smaller
        [70, 10, 40, 70, *([0] * 10), 0.9],   # area 2800, larger
    ]
    monkeypatch.setattr(cv2, "FaceDetectorYN_create", lambda *a, **k: _StubFaceDetector(rows))
    client = create_app({"TESTING": True}).test_client()

    response = client.post(
        "/pipeline/03_segmentation/contours", json=_contours_body()
    )

    assert response.status_code == 200
    assert response.json["stage"] == "03_segmentation"
    assert response.json["operation"] == "contours"
    assert response.json["metrics"] == {"object_count": 2}
    assert [
        {key: item[key] for key in ("x", "y", "width", "height")}
        for item in response.json["objects"]
    ] == [
        {"x": 70, "y": 10, "width": 40, "height": 70},
        {"x": 10, "y": 20, "width": 30, "height": 40},
    ]
    assert response.json["objects"][0]["area"] > response.json["objects"][1]["area"]
    assert response.json["objects"][0]["confidence"] == pytest.approx(0.9)


def test_contours_route_returns_200_and_empty_list_when_no_face_found():
    # the real YuNet model genuinely finds nothing in a blank synthetic image —
    # no monkeypatch needed, this exercises the real detector
    body = _contours_body()
    response = create_app({"TESTING": True}).test_client().post(
        "/pipeline/03_segmentation/contours", json=body
    )
    assert response.status_code == 200
    assert response.json["objects"] == []
    assert response.json["metrics"] == {"object_count": 0}


@pytest.mark.parametrize("params", [
    [],
    {"confidence_min": True},
    {"confidence_min": -0.01},
    {"confidence_min": 1.01},
    {"min_size": True},
    {"min_size": -1},
])
def test_contours_route_rejects_invalid_parameters(params):
    if isinstance(params, dict):
        body = _contours_body(**params)
    else:
        body = {"image": _encode_png(_blank_image()), "params": params}
    response = create_app({"TESTING": True}).test_client().post(
        "/pipeline/03_segmentation/contours", json=body
    )
    assert response.status_code == 400
    assert "error" in response.json


@pytest.mark.parametrize("body", [
    None,
    [],
    {"image": 123},
    {"image": "not-base64!!!"},
    {"image": base64.b64encode(b"not an image").decode("ascii")},
])
def test_contours_route_rejects_invalid_images_and_bodies(body):
    response = create_app({"TESTING": True}).test_client().post(
        "/pipeline/03_segmentation/contours", json=body
    )
    assert response.status_code == 400
    assert "error" in response.json


# --------------------------------------------- หน้า "ลบพื้นหลัง" (ลากกรอบแล้วกดลบ)

def _decode_png_with_alpha(image_b64):
    raw = base64.b64decode(image_b64, validate=True)
    return cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_UNCHANGED)


def _remove_bg_body(region=None):
    params = {"region": region if region is not None else {"x": 8, "y": 8, "width": 8, "height": 8}}
    return {"image": _encode_png(_checkerboard()), "params": params}


def test_remove_background_route_retains_foreground_object_and_erases_background():
    """[กรณีทดสอบ]: ลบพื้นหลังต้องคงตัววัตถุในกรอบไว้ (alpha 255) และทำให้พื้นหลังรอบนอกโปร่งใส (alpha 0)"""
    client = create_app({"TESTING": True}).test_client()

    response = client.post("/pipeline/03_segmentation/remove-background", json=_remove_bg_body())

    assert response.status_code == 200
    assert response.json["stage"] == "03_segmentation"
    assert response.json["operation"] == "remove-background"
    result = _decode_png_with_alpha(response.json["image"])
    assert result.shape == (24, 24, 4)
    alpha = result[:, :, 3]

    # region = {x:8, y:8, width:8, height:8}
    assert alpha[12, 12] == 255, "ตัววัตถุภายในกรอบที่เลือกต้องคงอยู่ (ทึบแสง)"
    assert alpha[0, 0] == 0, "นอกกรอบที่เลือก (พื้นหลัง) ต้องถูกลบเป็นโปร่งใส"

    erased = int(np.count_nonzero(alpha == 0))
    assert erased > 0, "ต้องมีการลบพื้นหลังให้โปร่งใส"
    assert response.json["metrics"] == {"erased_pixels": erased}


def test_remove_background_route_astronaut_keeps_person_and_removes_background():
    """[กรณีทดสอบ]: ทดสอบกับภาพ astronaut.png (skimage) ตามเงื่อนไขใน Issue #218
    ลากกรอบ (60, 0, 400, 512) รอบตัวคน -> คนต้องอยู่ (alpha 255) พื้นหลังมุมภาพต้องโปร่งใส (alpha 0)
    """
    import skimage.data
    client = create_app({"TESTING": True}).test_client()
    astronaut = cv2.cvtColor(skimage.data.astronaut(), cv2.COLOR_RGB2BGR)
    body = {
        "image": _encode_png(astronaut),
        "params": {"region": {"x": 60, "y": 0, "width": 400, "height": 512}},
    }

    response = client.post("/pipeline/03_segmentation/remove-background", json=body)
    assert response.status_code == 200
    alpha = _decode_png_with_alpha(response.json["image"])[:, :, 3]

    assert alpha[256, 260] == 255, "กลางตัวคน (260, 256) ต้องยังอยู่ (alpha 255)"
    assert alpha[5, 5] == 0, "มุมพื้นหลัง (5, 5) ต้องโปร่งใส (alpha 0)"


def test_remove_background_route_never_retains_outside_region():
    """[กรณีทดสอบ]: กรอบเล็กมาก (1x1) ต้องตัดพื้นหลังรอบนอกทั้งหมดให้โปร่งใส ไม่ล้นออกนอกกรอบ"""
    client = create_app({"TESTING": True}).test_client()
    body = {
        "image": _encode_png(_checkerboard()),
        "params": {"region": {"x": 12, "y": 12, "width": 1, "height": 1}},
    }

    response = client.post("/pipeline/03_segmentation/remove-background", json=body)

    assert response.status_code == 200
    alpha = _decode_png_with_alpha(response.json["image"])[:, :, 3]
    # จุดที่เลือก 1x1 ต้องถูกเก็บไว้
    assert alpha[12, 12] == 255, "พิกเซลในกรอบที่เลือกต้องถูกเก็บไว้"
    # เพื่อนบ้านทั้ง 4 ทิศนอกกรอบ 1x1 ต้องโปร่งใส (เป็นพื้นหลัง)
    assert alpha[11, 12] == 0, "พิกเซลด้านบนนอกกรอบต้องโปร่งใส"
    assert alpha[13, 12] == 0, "พิกเซลด้านล่างนอกกรอบต้องโปร่งใส"
    assert alpha[12, 11] == 0, "พิกเซลด้านซ้ายนอกกรอบต้องโปร่งใส"
    assert alpha[12, 13] == 0, "พิกเซลด้านขวานอกกรอบต้องโปร่งใส"


def test_remove_background_route_preserves_previously_erased_area_on_repeat():
    """[กรณีทดสอบ]: ลบพื้นหลังซ้ำรอบสองต้องไม่ทำให้พื้นที่ที่โปร่งใสไปแล้วในรอบแรกกลับมาทึบแสง"""
    client = create_app({"TESTING": True}).test_client()
    original = _checkerboard()

    first = client.post("/pipeline/03_segmentation/remove-background", json={
        "image": _encode_png(original),
        "params": {"region": {"x": 2, "y": 2, "width": 6, "height": 6}},
    })
    assert first.status_code == 200
    first_png_b64 = first.json["image"]
    first_alpha = _decode_png_with_alpha(first_png_b64)[:, :, 3]
    assert first_alpha[0, 0] == 0, "setup: รอบแรกต้องลบพื้นหลังนอกกรอบสำเร็จ"

    # ส่งผลลัพธ์รอบแรกกลับเข้าไปประมวลผลซ้ำ
    second = client.post("/pipeline/03_segmentation/remove-background", json={
        "image": first_png_b64,
        "params": {"region": {"x": 2, "y": 2, "width": 6, "height": 6}},
    })
    assert second.status_code == 200
    second_alpha = _decode_png_with_alpha(second.json["image"])[:, :, 3]

    assert second_alpha[0, 0] == 0, "พื้นที่ที่โปร่งใสไปแล้วในรอบแรกต้องยังโปร่งใสอยู่ ไม่กลับมาทึบแสง"


@pytest.mark.parametrize("params", [
    [],
    {},
    {"region": None},
    {"region": {"x": 0, "y": 0, "width": 5}},
    {"region": {"x": True, "y": 0, "width": 5, "height": 5}},
    {"region": {"x": -1, "y": 0, "width": 5, "height": 5}},
    {"region": {"x": 0, "y": 0, "width": 0, "height": 5}},
    {"region": {"x": 20, "y": 0, "width": 5, "height": 5}},
    {"region": {"x": 0, "y": 20, "width": 5, "height": 5}},
])
def test_remove_background_route_rejects_invalid_parameters(params):
    body = {"image": _encode_png(_checkerboard()), "params": params}
    response = create_app({"TESTING": True}).test_client().post(
        "/pipeline/03_segmentation/remove-background", json=body
    )
    assert response.status_code == 400
    assert "error" in response.json


@pytest.mark.parametrize("body", [
    None,
    [],
    {"image": 123},
    {"image": "not-base64!!!"},
    {"image": base64.b64encode(b"not an image").decode("ascii")},
])
def test_remove_background_route_rejects_invalid_images_and_bodies(body):
    response = create_app({"TESTING": True}).test_client().post(
        "/pipeline/03_segmentation/remove-background", json=body
    )
    assert response.status_code == 400
    assert "error" in response.json
