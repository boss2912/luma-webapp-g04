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

    forge_url = _get_forge_endpoint()
    logger.info(f"[generate] user={current_user.id} prompt='{prompt[:50]}' → {forge_url}")

    try:
        response = requests.post(
            forge_url,
            json={
                "prompt": prompt,
                "steps": 20,
                "width": 512,
                "height": 512,
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


def _get_owned_asset_or_404(asset_id):
    """
    ดึง Asset ที่ current_user เป็นเจ้าของเท่านั้น — ใช้ร่วมกันทั้ง get_asset_image()
    และ delete_asset() กันโค้ดซ้ำ
    ตอบ 404 (ไม่ใช่ 403) ทั้งกรณี "ไม่มี asset นี้" และ "มีแต่ไม่ใช่ของเรา"
    เพื่อไม่บอกผู้โจมตีว่า asset_id นั้นมีอยู่จริงหรือเปล่า — ลดข้อมูลที่รั่วไหลออกไป
    """
    # db.session.get() แทน Asset.query.get() ที่ deprecated ใน SQLAlchemy 2.x
    # (ดู models.py: load_user() เตือนเรื่องเดียวกันนี้ไว้แล้วสำหรับ User)
    asset = db.session.get(Asset, asset_id)
    if asset is None or asset.user_id != current_user.id:
        abort(404)
    return asset


@api_bp.route("/assets/<int:asset_id>/image", methods=["GET"])
@login_required
def get_asset_image(asset_id):
    """
    Fix F05 (IDOR): เดิมรูปถูกเก็บใน app/static/generated/ ทำให้ Flask เสิร์ฟ
    ให้ทุกคนที่รู้/เดา URL เห็นได้เลย ไม่ต้อง login ไม่ต้องเป็นเจ้าของ
    ตอนนี้ต้อง (1) login และ (2) เป็นเจ้าของ asset นั้นเท่านั้นถึงจะดูรูปได้
    """
    asset = _get_owned_asset_or_404(asset_id)
    return send_from_directory(UPLOAD_FOLDER, os.path.basename(asset.filename))


@api_bp.route("/assets/<int:asset_id>", methods=["DELETE"])
@login_required
def delete_asset(asset_id):
    """
    Issue #3: ลบ asset ของตัวเอง — ลบทั้งไฟล์ภาพบนดิสก์และแถวใน DB
    หมายเหตุ CSRF: route นี้อยู่ใต้ api_bp ที่ยกเว้น CSRF ทั้ง blueprint (ดู
    app/__init__.py) แต่ DELETE ไม่ใช่ "simple method" ตาม Fetch spec เลยต้อง
    ผ่าน CORS preflight (OPTIONS) ก่อนเสมอ — เว็บนี้ไม่ได้ตั้งค่า CORS ให้ origin
    อื่นเลย เบราว์เซอร์จึงบล็อก cross-site DELETE ไว้ตั้งแต่ขั้น preflight แล้ว
    โดยไม่ต้องพึ่ง csrf_token
    """
    asset = _get_owned_asset_or_404(asset_id)

    filepath = os.path.join(UPLOAD_FOLDER, os.path.basename(asset.filename))
    try:
        os.remove(filepath)
    except FileNotFoundError:
        # ไฟล์หายไปจากดิสก์แล้วแต่แถว DB ยังอยู่ — ไม่ต้อง fail การลบ แค่ log ไว้
        logger.warning(f"[delete_asset] file already missing on disk: {filepath}")

    db.session.delete(asset)
    db.session.commit()
    logger.info(f"[delete_asset] user={current_user.id} deleted asset_id={asset_id}")

    return jsonify({"status": "deleted", "asset_id": asset_id})

