"""
LUMA Authentication Routes
Endpoints สำหรับสมัครสมาชิก เข้าสู่ระบบ ออกจากระบบ และตรวจสถานะ Session
"""

from flask import Blueprint, jsonify, request, session

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """POST /api/auth/register — สมัครสมาชิกใหม่"""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    display_name = data.get("displayName", "").strip() or data.get("username", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "กรุณากรอกข้อมูลให้ครบถ้วน / Missing required fields"}), 400

    if len(password) < 8:
        return jsonify({"error": "รหัสผ่านต้องยาวอย่างน้อย 8 ตัวอักษร / Password must be at least 8 characters"}), 400

    # ในอนาคตเมื่อมี User Model จะทำการ hash password และบันทึก
    # สำหรับรอบนี้ รองรับการตอบกลับ JSON ตาม API Contract
    return jsonify({
        "status": "success",
        "message": "สมัครสมาชิกสำเร็จ / Registration successful",
        "user": {
            "email": email,
            "displayName": display_name or email.split("@")[0],
        },
    }), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    """POST /api/auth/login — เข้าสู่ระบบ"""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "อีเมลหรือรหัสผ่านไม่ถูกต้อง / Invalid email or password"}), 400

    # จำลองการสร้าง session
    session["user_email"] = email
    session.permanent = True

    return jsonify({
        "status": "success",
        "message": "เข้าสู่ระบบสำเร็จ / Login successful",
        "user": {
            "email": email,
            "displayName": email.split("@")[0],
        },
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """POST /api/auth/logout — ออกจากระบบ"""
    session.clear()
    return jsonify({
        "status": "success",
        "message": "ออกจากระบบสำเร็จ / Logged out successfully",
    }), 200


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """GET /api/auth/me — ตรวจสอบผู้ใช้ปัจจุบัน"""
    user_email = session.get("user_email")
    if not user_email:
        return jsonify({"error": "ยังไม่ได้เข้าสู่ระบบ / Unauthorized"}), 401

    return jsonify({
        "email": user_email,
        "displayName": user_email.split("@")[0],
    }), 200
