"""
LUMA API Routes
Endpoint สร้างภาพ AI (Issue #22)
"""

from flask import Blueprint, current_app, jsonify, request
from app.models import db, Asset
from app.services.forge_client import generate_image, ForgeClientError

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/ping", methods=["GET"])
def ping():
    """GET /api/ping — ตรวจสอบการทำงานของ Blueprint api (Issue #47)"""
    return jsonify({"status": "ok", "blueprint": "api"}), 200


@api_bp.route("/generate", methods=["POST"])
def handle_generate():
    """POST /api/generate — สั่งสร้างภาพใหม่ผ่าน Forge AI หรือ Mock Server (Issue #22)"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "คำขอต้องเป็น JSON / Request must be JSON"}), 400

    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "กรุณาระบุคำบรรยายภาพ (prompt) / prompt is required"}), 400

    negative_prompt = data.get("negative_prompt", "").strip()

    try:
        steps = int(data.get("steps", 20))
        if steps < 1 or steps > 100:
            return jsonify({"error": "steps ต้องอยู่ระหว่าง 1-100"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "steps ต้องเป็นตัวเลขจำนวนเต็ม / steps must be an integer"}), 400

    try:
        cfg_scale = float(data.get("cfg_scale", 8.0))
        if cfg_scale < 1.0 or cfg_scale > 30.0:
            return jsonify({"error": "cfg_scale ต้องอยู่ระหว่าง 1.0-30.0"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "cfg_scale ต้องเป็นตัวเลข / cfg_scale must be a number"}), 400

    sampler_name = data.get("sampler_name", "DPM++ 2M Karras")

    try:
        seed = int(data.get("seed", -1))
    except (ValueError, TypeError):
        return jsonify({"error": "seed ต้องเป็นตัวเลขจำนวนเต็ม / seed must be an integer"}), 400

    try:
        width = int(data.get("width", 512))
        height = int(data.get("height", 512))
    except (ValueError, TypeError):
        return jsonify({"error": "width และ height ต้องเป็นจำนวนเต็ม"}), 400

    try:
        relative_path, seed_used = generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            steps=steps,
            cfg_scale=cfg_scale,
            sampler_name=sampler_name,
            seed=seed,
            width=width,
            height=height,
        )
    except ForgeClientError as e:
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        current_app.logger.error(f"เกิดข้อผิดพลาดในการสร้างภาพ: {e}", exc_info=True)
        return jsonify({"error": "เกิดข้อผิดพลาดในการติดต่อ AI Engine / Internal Server Error"}), 500

    try:
        new_asset = Asset(
            prompt=prompt,
            file_path=relative_path,
        )
        db.session.add(new_asset)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"ไม่สามารถบันทึกข้อมูล Asset: {e}", exc_info=True)
        return jsonify({"error": "ไม่สามารถบันทึกข้อมูลลงฐานข้อมูลได้ / Database error"}), 500

    return jsonify({
        "status": "success",
        "asset_id": new_asset.id,
        "image_url": f"/api/assets/{new_asset.id}/image",
    }), 200
