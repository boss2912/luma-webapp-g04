"""
LUMA General API Routes
Endpoints สำหรับสร้างภาพ จัดการคลังผลงาน (Assets)
"""

import os
from flask import Blueprint, current_app, jsonify, request, send_file
from app.models import db, Asset
from app.services.forge_client import generate_image, ForgeClientError

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/generate", methods=["POST"])
def handle_generate():
    """POST /api/generate — สร้างภาพใหม่จาก Prompt"""
    data = request.get_json(silent=True) or {}

    prompt = data.get("prompt")
    if not prompt or not isinstance(prompt, str) or not prompt.strip():
        return jsonify({"error": "กรุณาระบุ prompt / Prompt is required"}), 400

    prompt = prompt.strip()
    negative_prompt = data.get("negative_prompt", "")
    if not isinstance(negative_prompt, str):
        negative_prompt = ""

    # Validation: ตรวจสอบชนิดข้อมูล (ระวัง bool ใน python เป็น subclass ของ int)
    steps = data.get("steps", 20)
    if isinstance(steps, bool) or not isinstance(steps, int) or not (1 <= steps <= 100):
        return jsonify({"error": "steps ต้องเป็นตัวเลข 1-100 / steps must be an integer between 1 and 100"}), 400

    cfg_scale = data.get("cfg_scale", 8.0)
    if isinstance(cfg_scale, bool) or not isinstance(cfg_scale, (int, float)) or not (1.0 <= float(cfg_scale) <= 30.0):
        return jsonify({"error": "cfg_scale ต้องอยู่ระหว่าง 1-30 / cfg_scale must be between 1 and 30"}), 400

    sampler_name = data.get("sampler_name", "DPM++ 2M Karras")
    seed = data.get("seed", -1)
    if isinstance(seed, bool) or not isinstance(seed, int):
        seed = -1

    width = data.get("width", 512)
    height = data.get("height", 512)
    if isinstance(width, bool) or not isinstance(width, int) or width not in (512, 768, 1024):
        width = 512
    if isinstance(height, bool) or not isinstance(height, int) or height not in (512, 768, 1024):
        height = 512

    try:
        relative_path, _ = generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            steps=steps,
            cfg_scale=float(cfg_scale),
            sampler_name=str(sampler_name),
            seed=seed,
            width=width,
            height=height,
        )
    except ForgeClientError as e:
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        current_app.logger.exception("เกิดข้อผิดพลาดในการสร้างภาพ:")
        return jsonify({"error": f"เกิดข้อผิดพลาดภายในระบบ: {e} / Internal server error"}), 500

    # บันทึกข้อมูลลงฐานข้อมูล
    asset = Asset(prompt=prompt, file_path=relative_path)
    db.session.add(asset)
    db.session.commit()

    return jsonify({
        "status": "success",
        "asset_id": asset.id,
        "image_url": f"/api/assets/{asset.id}/image",
    }), 200


@api_bp.route("/assets", methods=["GET"])
def list_assets():
    """GET /api/assets — ดึงรายการภาพทั้งหมดเรียงจากใหม่ไปเก่า"""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    q = request.args.get("q", "", type=str).strip()

    query = Asset.query
    if q:
        query = query.filter(Asset.prompt.ilike(f"%{q}%"))

    query = query.order_by(Asset.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [item.to_dict() for item in pagination.items]

    return jsonify({
        "items": items,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
    }), 200


@api_bp.route("/assets/<int:asset_id>/image", methods=["GET"])
def get_asset_image(asset_id: int):
    """GET /api/assets/<asset_id>/image — ให้บริการดาวน์โหลด/แสดงไฟล์ภาพ"""
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({"error": "ไม่พบภาพที่ระบุ / Asset not found"}), 404

    # แปลง relative path เป็น absolute path
    full_path = os.path.join(current_app.instance_path, asset.file_path)
    if not os.path.exists(full_path):
        return jsonify({"error": "ไฟล์ภาพสูญหาย / Image file not found on disk"}), 404

    return send_file(full_path, mimetype="image/png")


@api_bp.route("/assets/<int:asset_id>", methods=["DELETE"])
def delete_asset(asset_id: int):
    """DELETE /api/assets/<asset_id> — ลบรายการภาพและไฟล์"""
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({"error": "ไม่พบภาพที่ระบุ / Asset not found"}), 404

    full_path = os.path.join(current_app.instance_path, asset.file_path)
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
        except OSError:
            current_app.logger.warning(f"ไม่สามารถลบไฟล์ภาพบนดิสก์ได้: {full_path}")

    db.session.delete(asset)
    db.session.commit()

    return jsonify({"status": "deleted", "asset_id": asset_id}), 200
