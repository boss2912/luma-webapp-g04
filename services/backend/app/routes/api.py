"""
LUMA API Routes
Blueprint สำหรับจัดการ API สร้างภาพและคลังผลงาน
Issue #47 — Blueprint Modular Architecture
"""

from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/ping", methods=["GET"])
def ping():
    """GET /api/ping — ตรวจสอบการทำงานของ Blueprint api"""
    return jsonify({"status": "ok", "blueprint": "api"}), 200
