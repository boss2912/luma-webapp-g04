"""
API Blueprint
-------------
Input   : JSON prompt จาก frontend (เช่น {"prompt": "a cat wizard"})
Process : ยิง request ต่อไปที่ Forge AI service (คนที่ 3 เป็นคนเปิด endpoint นี้ไว้)
Output  : JSON ที่มี path/URL ของภาพที่ generate เสร็จ แล้วบันทึกลง DB (Asset)
"""

import os
import base64
import uuid
import requests
from flask import Blueprint, request, jsonify, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from app import db
from app.models import Asset
from app.utils.logger import get_logger

logger = get_logger(__name__)
api_bp = Blueprint("api", __name__)

# Issue #5: ขอบเขตพารามิเตอร์ที่ยอมรับ — เช็คก่อนยิงต่อไปที่ Forge AI เสมอ
ALLOWED_DIMENSIONS = (512, 768, 1024)
MIN_STEPS, MAX_STEPS = 1, 50
DEFAULT_STEPS = 20
MIN_CFG_SCALE, MAX_CFG_SCALE = 1, 30
DEFAULT_CFG_SCALE = 7

# Fix F05 (IDOR): เดิมเก็บใน app/static/generated/ ซึ่ง Flask เสิร์ฟให้ใครก็ได้
# เห็นผ่าน URL ตรงๆ โดยไม่เช็ค login เลย (แค่รู้/เดา URL ก็ดูรูปคนอื่นได้)
# ย้ายออกมานอก static/ แล้วบังคับให้ดูผ่าน route get_asset_image() ที่เช็ค
# ownership เท่านั้น — ใช้ absolute path ยึดกับตำแหน่งไฟล์นี้เอง (ไม่ใช่ relative
# path ที่พึ่ง current working directory ตอนรัน ซึ่งเคยทำให้ route หาไฟล์ไม่เจอ)
UPLOAD_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "generated")
)


def _get_forge_endpoint() -> str:
    """อ่าน FORGE_AI_ENDPOINT จาก config (ป้องกัน hardcode URL)"""
    return current_app.config.get(
        "FORGE_AI_ENDPOINT", "http://localhost:7860/sdapi/v1/txt2img"
    )


def _save_base64_image(b64_string: str, filename: str) -> str:
    """
    แปลง base64 string → บันทึกเป็นไฟล์ภาพ
    Return: relative path สำหรับ serve ผ่าน Flask static
    """
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(b64_string))
    # คืนแค่ชื่อไฟล์ (ไม่ผูกกับ static/ อีกต่อไป — ดูรูปต้องผ่าน
    # get_asset_image() ที่เช็ค ownership เท่านั้น)
    return filename


def _validate_generate_params(data):
    """
    Issue #5: ตรวจ negative_prompt / steps / cfg_scale / width / height ก่อนส่งต่อ
    Forge AI เสมอ — ไม่มี field ไหนที่จำเป็นต้องส่งมา (ทุกตัวมีค่า default)
    Return: (params dict, error message หรือ None)
    """
    params = {
        "negative_prompt": "",
        "steps": DEFAULT_STEPS,
        "cfg_scale": DEFAULT_CFG_SCALE,
        "width": 512,
        "height": 512,
    }

    negative_prompt = data.get("negative_prompt", "")
    if negative_prompt is not None:
        if not isinstance(negative_prompt, str):
            return None, "negative_prompt ต้องเป็น string / negative_prompt must be a string"
        params["negative_prompt"] = negative_prompt.strip()

    if "steps" in data and data["steps"] is not None:
        steps = data["steps"]
        if not isinstance(steps, int) or isinstance(steps, bool) or not (MIN_STEPS <= steps <= MAX_STEPS):
            return None, f"steps ต้องเป็นจำนวนเต็มระหว่าง {MIN_STEPS}-{MAX_STEPS} / steps must be an integer between {MIN_STEPS} and {MAX_STEPS}"
        params["steps"] = steps

    if "cfg_scale" in data and data["cfg_scale"] is not None:
        cfg_scale = data["cfg_scale"]
        if not isinstance(cfg_scale, (int, float)) or isinstance(cfg_scale, bool) or not (MIN_CFG_SCALE <= cfg_scale <= MAX_CFG_SCALE):
            return None, f"cfg_scale ต้องเป็นตัวเลขระหว่าง {MIN_CFG_SCALE}-{MAX_CFG_SCALE} / cfg_scale must be a number between {MIN_CFG_SCALE} and {MAX_CFG_SCALE}"
        params["cfg_scale"] = cfg_scale

    for dim in ("width", "height"):
        if dim in data and data[dim] is not None:
            value = data[dim]
            if value not in ALLOWED_DIMENSIONS:
                allowed = "/".join(str(d) for d in ALLOWED_DIMENSIONS)
                return None, f"{dim} ต้องเป็นหนึ่งใน {allowed} / {dim} must be one of {allowed}"
            params[dim] = value

    return params, None


@api_bp.route("/generate", methods=["POST"])
@login_required
def generate_image():
    # silent=True: ถ้า body ไม่ใช่ JSON ที่ parse ได้ จะได้ None แทนที่จะโยน
    # exception ขึ้นมาเป็น 500 — เช็คแล้วตอบ 400 ที่อ่านง่ายกว่าแทน
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "ต้องส่ง JSON body / request body must be JSON"}), 400

    prompt = data.get("prompt", "")
    # Fix F04: เดิมถ้า prompt ไม่ใช่ string (เช่น {"prompt": 12345}) การเรียก
    # .strip() จะ crash เป็น 500 — เช็ค type ก่อนเสมอ
    if not isinstance(prompt, str):
        return jsonify({"error": "prompt ต้องเป็น string / prompt must be a string"}), 400
    prompt = prompt.strip()

    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    gen_params, error = _validate_generate_params(data)
    if error:
        return jsonify({"error": error}), 400

    forge_url = _get_forge_endpoint()
    logger.info(f"[generate] user={current_user.id} prompt='{prompt[:50]}' → {forge_url}")

    try:
        response = requests.post(
            forge_url,
            json={
                "prompt": prompt,
                **gen_params,
            },
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()

        # บันทึกรูปภาพจาก base64 (Forge AI ส่งกลับมาเป็น list)
        images = result.get("images", [])
        if not images:
            return jsonify({"error": "Forge AI ไม่ส่งรูปกลับมา"}), 502

        # Fix F11: เดิมใช้ int(time.time()) ความละเอียดแค่ระดับวินาที ถ้ามีคน
        # generate 2 ครั้งในวินาทีเดียวกัน ไฟล์ชื่อชนกันและไฟล์เก่าถูกทับ
        # เปลี่ยนเป็น uuid4 ที่ไม่ซ้ำกันแทบจะแน่นอน
        filename = f"asset_{current_user.id}_{uuid.uuid4().hex[:12]}.png"
        saved_filename = _save_base64_image(images[0], filename)
        logger.info(f"[generate] saved image → {saved_filename}")

        asset = Asset(
            user_id=current_user.id,
            filename=saved_filename,
            prompt=prompt,
        )
        db.session.add(asset)
        db.session.commit()

        return jsonify({
            "status": "success",
            "asset_id": asset.id,
            "image_url": f"/api/assets/{asset.id}/image",
        })

    except requests.exceptions.ConnectionError:
        logger.error(f"[generate] Forge AI ไม่ตอบสนอง: {forge_url}")
        return jsonify({"error": f"เชื่อมต่อ Forge AI ไม่ได้ ({forge_url}) — ตรวจสอบว่า Stable Diffusion WebUI กำลังทำงานอยู่"}), 502
    except requests.exceptions.Timeout:
        logger.error("[generate] Forge AI timeout")
        return jsonify({"error": "Forge AI ใช้เวลานานเกินไป (timeout 120s)"}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"[generate] error: {e}")
        return jsonify({"error": f"Forge AI error: {str(e)}"}), 502


@api_bp.route("/assets", methods=["GET"])
@login_required
def list_assets():
    """ดึงรายการ Asset ทั้งหมดของ user ที่ login อยู่"""
    assets = Asset.query.filter_by(user_id=current_user.id).order_by(Asset.created_at.desc()).all()
    return jsonify([
        {
            "id": a.id,
            "filename": a.filename,
            "prompt": a.prompt,
            "tags": a.tags,
            "created_at": a.created_at.isoformat(),
            "image_url": f"/api/assets/{a.id}/image",
        }
        for a in assets
    ])


@api_bp.route("/assets/<int:asset_id>/image", methods=["GET"])
@login_required
def get_asset_image(asset_id):
    """
    Fix F05 (IDOR): เดิมรูปถูกเก็บใน app/static/generated/ ทำให้ Flask เสิร์ฟ
    ให้ทุกคนที่รู้/เดา URL เห็นได้เลย ไม่ต้อง login ไม่ต้องเป็นเจ้าของ
    ตอนนี้ต้อง (1) login และ (2) เป็นเจ้าของ asset นั้นเท่านั้นถึงจะดูรูปได้
    """
    # db.session.get() แทน Asset.query.get() ที่ deprecated ใน SQLAlchemy 2.x
    # (ดู models.py: load_user() เตือนเรื่องเดียวกันนี้ไว้แล้วสำหรับ User)
    asset = db.session.get(Asset, asset_id)
    if asset is None:
        abort(404)
    if asset.user_id != current_user.id:
        # ตอบ 404 (ไม่ใช่ 403) เพื่อไม่บอกผู้โจมตีว่า asset_id นี้มีอยู่จริง
        # แค่เป็นของคนอื่น — ลดข้อมูลที่รั่วไหลออกไป
        abort(404)
    return send_from_directory(UPLOAD_FOLDER, os.path.basename(asset.filename))

