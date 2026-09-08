"""
LUMA Auth Routes
Endpoints สำหรับระบบสมาชิก Authentication (Issue #50 Login / Logout / Session)
"""

from flask import Blueprint, jsonify, request, session

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """POST /api/auth/register — สมัครสมาชิกใหม่"""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    display_name = data.get("displayName", "").strip()
    password = data.get("password", "")

    if not email or "@" not in email:
        return jsonify({"error": "กรุณาระบุอีเมลที่ถูกต้อง / Valid email required"}), 400
    if not display_name:
        return jsonify({"error": "กรุณาระบุชื่อแสดงผล / displayName required"}), 400
    if not password or len(password) < 8:
        return jsonify({"error": "รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร / Password must be at least 8 chars"}), 400

    return jsonify({
        "status": "success",
        "message": "สมัครสมาชิกสำเร็จ",
        "user": {"email": email, "displayName": display_name},
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """POST /api/auth/login — เข้าสู่ระบบและสร้าง Session (Issue #50)"""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "กรุณาระบุอีเมลและรหัสผ่าน / Email and password required"}), 400

    # ตรวจสอบรหัสผ่านขั้นต่ำ (หรือเทียบกับฐานข้อมูล)
    if len(password) < 8:
        return jsonify({"error": "อีเมลหรือรหัสผ่านไม่ถูกต้อง / Invalid credentials"}), 401

    display_name = email.split("@")[0].capitalize()

    # บันทึกข้อมูลลงใน Flask Session
    session["user"] = {
        "email": email,
        "displayName": display_name,
    }

    return jsonify({
        "status": "success",
        "message": "เข้าสู่ระบบสำเร็จ",
        "user": session["user"],
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """POST /api/auth/logout — ออกจากระบบและล้าง Session (Issue #50)"""
    session.pop("user", None)
    return jsonify({
        "status": "success",
        "message": "ออกจากระบบสำเร็จ",
    }), 200


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """GET /api/auth/me — ตรวจสอบข้อมูลผู้ใช้ที่ล็อกอินอยู่ (Issue #50)"""
    user = session.get("user")
    if not user:
        return jsonify({"error": "ยังไม่ได้เข้าสู่ระบบ / Unauthorized"}), 401

    return jsonify(user), 200
