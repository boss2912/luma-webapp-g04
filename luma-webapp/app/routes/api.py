"""
API Blueprint
-------------
Input   : JSON prompt จาก frontend (เช่น {"prompt": "a cat wizard"})
Process : ยิง request ต่อไปที่ Forge AI service (คนที่ 3 เป็นคนเปิด endpoint นี้ไว้)
Output  : JSON ที่มี path/URL ของภาพที่ generate เสร็จ แล้วบันทึกลง DB (Asset)
"""

import os
import base64
import time
import requests
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Asset
from app.utils.logger import get_logger

logger = get_logger(__name__)
api_bp = Blueprint("api", __name__)

# โฟลเดอร์สำหรับเก็บรูปที่ generate (สร้างอัตโนมัติถ้าไม่มี)
UPLOAD_FOLDER = os.path.join("app", "static", "generated")


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
    # คืน path แบบ URL-friendly (สำหรับ url_for('static', ...))
    return f"generated/{filename}"


@api_bp.route("/generate", methods=["POST"])
@login_required
def generate_image():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()

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

        filename = f"asset_{current_user.id}_{int(time.time())}.png"
        relative_path = _save_base64_image(images[0], filename)
        logger.info(f"[generate] saved image → {relative_path}")

        asset = Asset(
            user_id=current_user.id,
            filename=relative_path,
            prompt=prompt,
        )
        db.session.add(asset)
        db.session.commit()

        return jsonify({
            "status": "success",
            "asset_id": asset.id,
            "image_url": f"/static/{relative_path}",
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
        }
        for a in assets
    ])

