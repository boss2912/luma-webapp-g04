"""
LUMA Auth Routes
Blueprint สำหรับจัดการระบบ Authentication
Issue #47 — Blueprint Modular Architecture
"""

from flask import Blueprint, jsonify

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/ping", methods=["GET"])
def ping():
    """GET /api/auth/ping — ตรวจสอบการทำงานของ Blueprint auth"""
    return jsonify({"status": "ok", "blueprint": "auth"}), 200
