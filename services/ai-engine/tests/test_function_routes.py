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


def test_remove_background_route_erases_an_ellipse_inscribed_in_the_region_not_the_whole_box():
    """[กรณีทดสอบ]: ลบเป็นวงรี/วงกลมที่แนบในกรอบที่ลาก ไม่ใช่ทั้งกรอบสี่เหลี่ยม (ตามที่ผู้ใช้ขอ)"""
    client = create_app({"TESTING": True}).test_client()

    response = client.post("/pipeline/03_segmentation/remove-background", json=_remove_bg_body())

    assert response.status_code == 200
    assert response.json["stage"] == "03_segmentation"
    assert response.json["operation"] == "remove-background"
    result = _decode_png_with_alpha(response.json["image"])
    assert result.shape == (24, 24, 4)
    alpha = result[:, :, 3]

    # region = {x:8, y:8, width:8, height:8} -> วงกลมรัศมี 4 จุดศูนย์กลาง (12, 12)
    assert alpha[12, 12] == 0, "จุดกึ่งกลางวงกลมต้องถูกลบเป็นโปร่งใส"
    assert alpha[8, 8] == 255, "มุมของกรอบสี่เหลี่ยมต้องไม่ถูกลบ เพราะอยู่นอกวงกลมที่แนบใน"
    assert alpha[0, 0] == 255, "นอกกรอบทั้งหมดต้องทึบแสงเหมือนเดิม"

    erased = int(np.count_nonzero(alpha == 0))
    assert 0 < erased < 64, "พื้นที่ที่ลบต้องน้อยกว่าทั้งกรอบสี่เหลี่ยม (8x8=64) เพราะเป็นวงกลมข้างใน"
    assert response.json["metrics"] == {"erased_pixels": erased}


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
