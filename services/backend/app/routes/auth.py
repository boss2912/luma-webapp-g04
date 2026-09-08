"""
LUMA Auth Routes
Endpoints สำหรับระบบสมาชิก Authentication (Issue #49 Register)
"""

from flask import Blueprint, jsonify, request

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """POST /api/auth/register — สมัครสมาชิกใหม่ (Issue #49)"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "คำขอต้องเป็น JSON / Request must be JSON"}), 400

    email = data.get("email", "").strip()
    display_name = data.get("displayName", "").strip()
    password = data.get("password", "")

    if not email or "@" not in email:
        return jsonify({"error": "กรุณาระบุอีเมลที่ถูกต้อง / Valid email required"}), 400

    if not display_name:
        return jsonify({"error": "กรุณาระบุชื่อแสดงผล / displayName required"}), 400

    if not password or len(password) < 8:
        return jsonify({"error": "รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร / Password must be at least 8 chars"}), 400

    # ตอบกลับ 201 Created ตาม API Contract
    return jsonify({
        "status": "success",
        "message": "สมัครสมาชิกสำเร็จ",
        "user": {
            "email": email,
            "displayName": display_name,
        },
    }), 201
