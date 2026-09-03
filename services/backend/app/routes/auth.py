"""
LUMA Authentication Routes
Endpoints สำหรับสมัครสมาชิก เข้าสู่ระบบ ออกจากระบบ และตรวจสถานะ Session
Issue #50 & #51 — ระบบความปลอดภัย Rate Limiting และ Password Verification
"""

import time
from collections import defaultdict
from flask import Blueprint, current_app, jsonify, request, session

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# In-Memory Rate Limiter สำหรับป้องกัน Brute-Force Login (IP -> [timestamps])
_login_attempts = defaultdict(list)


def check_rate_limit(client_id: str, max_attempts: int = 5, window_seconds: int = 60) -> bool:
    """ตรวจสอบว่า client ทำการล็อกอินผิดเกินโควต้าหรือไม่ (Sliding Window)"""
    now = time.time()
    # กรองเฉพาะ attempt ที่เกิดขึ้นภายใน window ล่าสุด
    _login_attempts[client_id] = [
        t for t in _login_attempts[client_id] if now - t < window_seconds
    ]
    return len(_login_attempts[client_id]) < max_attempts


def record_failed_attempt(client_id: str):
    """บันทึกเวลาที่ล็อกอินผิดพลาด"""
    _login_attempts[client_id].append(time.time())


def clear_failed_attempts(client_id: str):
    """ล้างประวัติเมื่อล็อกอินสำเร็จ"""
    if client_id in _login_attempts:
        del _login_attempts[client_id]


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
    """POST /api/auth/login — เข้าสู่ระบบพร้อมระบบ Rate Limiting ป้องกัน Brute-force"""
    client_ip = request.remote_addr or "127.0.0.1"
    max_attempts = current_app.config.get("RATE_LIMIT_MAX_ATTEMPTS", 5)
    window_seconds = current_app.config.get("RATE_LIMIT_WINDOW_SECONDS", 60)

    # 1. ตรวจสอบ Rate Limit
    if not check_rate_limit(client_ip, max_attempts=max_attempts, window_seconds=window_seconds):
        return jsonify({
            "error": "พยายามเข้าสู่ระบบบ่อยเกินไป กรุณารอสักครู่ / Too many login attempts. Please try again later.",
            "retry_after_seconds": window_seconds,
        }), 429

    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        record_failed_attempt(client_ip)
        return jsonify({"error": "อีเมลหรือรหัสผ่านไม่ถูกต้อง / Invalid email or password"}), 400

    # เมื่อล็อกอินสำเร็จ ล้างประวัติการทำผิด
    clear_failed_attempts(client_ip)

    # บันทึก Session
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
    """POST /api/auth/logout — ออกจากระบบและล้าง Session"""
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
