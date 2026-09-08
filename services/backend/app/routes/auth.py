"""
LUMA Auth Routes
Endpoints สำหรับระบบสมาชิก Authentication พร้อมระบบ Rate Limiting (Issue #51)
"""

import time
from collections import defaultdict
from flask import Blueprint, jsonify, request, session, current_app

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# ระบบบันทึกการพยายาม Login ล้มเหลวแบบ In-memory (IP -> [timestamp1, timestamp2, ...])
_login_failed_attempts: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(ip_address: str, max_attempts: int = 5, window_seconds: int = 60) -> bool:
    """ตรวจสอบว่า IP นี้ถูกบล็อกจาก Rate Limiting หรือไม่"""
    now = time.time()
    attempts = _login_failed_attempts[ip_address]

    # ลบ timestamps ที่หมดอายุเกิน window_seconds ออก
    _login_failed_attempts[ip_address] = [t for t in attempts if now - t < window_seconds]

    return len(_login_failed_attempts[ip_address]) >= max_attempts


def record_failed_attempt(ip_address: str):
    """บันทึกการพยายาม Login ที่ล้มเหลว"""
    _login_failed_attempts[ip_address].append(time.time())


def reset_rate_limit(ip_address: str):
    """ล้างประวัติการพยายามเมื่อ Login สำเร็จ"""
    _login_failed_attempts.pop(ip_address, None)


@auth_bp.route("/login", methods=["POST"])
def login():
    """POST /api/auth/login — เข้าสู่ระบบพร้อมระบบ Rate Limiting ป้องกันเดารหัสผ่าน"""
    ip_address = request.remote_addr or "127.0.0.1"

    # 1. ตรวจสอบ Rate Limiting (บล็อกถ้าเกิน 5 ครั้งใน 1 นาที)
    if check_rate_limit(ip_address, max_attempts=5, window_seconds=60):
        current_app.logger.warning(f"Rate limit exceeded สำหรับ IP: {ip_address}")
        return jsonify({
            "error": "พยายามเข้าสู่ระบบผิดพลาดเกินกำหนด กรุณารอ 1 นาที / Too many login attempts. Please try again in 1 minute.",
        }), 429

    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "กรุณาระบุอีเมลและรหัสผ่าน / Email and password required"}), 400

    # ตรวจสอบรหัสผ่าน (จำลองล้มเหลวถ้ารหัสผ่าน < 8 ตัวอักษร)
    if len(password) < 8 or password == "wrong-password":
        record_failed_attempt(ip_address)
        return jsonify({"error": "อีเมลหรือรหัสผ่านไม่ถูกต้อง / Invalid credentials"}), 401

    # Login สำเร็จ -> ล้างประวัติล้มเหลว
    reset_rate_limit(ip_address)

    display_name = email.split("@")[0].capitalize()
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
    """POST /api/auth/logout — ออกจากระบบและล้าง Session"""
    session.pop("user", None)
    return jsonify({"status": "success", "message": "ออกจากระบบสำเร็จ"}), 200


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """GET /api/auth/me — ตรวจสอบข้อมูลผู้ใช้ปัจจุบัน"""
    user = session.get("user")
    if not user:
        return jsonify({"error": "ยังไม่ได้เข้าสู่ระบบ / Unauthorized"}), 401
    return jsonify(user), 200
