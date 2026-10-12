"""
LUMA Admin Routes
หน้าจัดการผู้ใช้ — ใช้ได้เฉพาะบัญชีที่ role = "admin"

มี 2 endpoint
    GET   /api/admin/users        ดูรายชื่อผู้ใช้ทั้งหมด
    PATCH /api/admin/users/<id>   แก้ชื่อ อีเมล หรือตั้งรหัสผ่านใหม่ให้ผู้ใช้

ไม่มี endpoint ไหนส่งรหัสผ่านออกไป เพราะตาราง users เก็บแค่ hash
ซึ่งแปลงกลับเป็นรหัสจริงไม่ได้ — admin ทำได้แค่ตั้งรหัสใหม่
"""

from flask import Blueprint, jsonify, request, session
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from app.models import User, db
from app.routes.api import ID
from app.routes.auth import _ALREADY_TAKEN, _invalid

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def admin_error():
    """เช็คว่าคนที่เรียกเป็น admin ไหม

    คืน None ถ้าเป็น admin (ทำงานต่อได้)
    ถ้าไม่ใช่ คืนคำตอบ error ที่ route ส่งกลับไปได้เลย
        401 = ยังไม่ได้ล็อกอิน
        403 = ล็อกอินแล้วแต่ไม่ใช่ admin

    อ่าน role จากฐานข้อมูลทุกครั้ง ไม่เก็บ role ไว้ใน session
    ถ้าเก็บใน session คนที่โดนถอนสิทธิ์จะยังเป็น admin ต่อจนกว่าจะออกจากระบบ
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "ยังไม่ได้เข้าสู่ระบบ / Unauthorized"}), 401

    user = db.session.get(User, user_id)
    if user is None or user.role != "admin":
        return jsonify({"error": "เฉพาะผู้ดูแลระบบ / Admin only"}), 403

    return None


def user_to_dict(user):
    """ข้อมูลผู้ใช้ 1 คนที่ส่งให้หน้า admin — ไม่มี password_hash"""
    return {
        "id": user.id,
        "displayName": user.username,
        "email": user.email,
        "role": user.role,
    }


@admin_bp.route("/users", methods=["GET"])
def list_users():
    """GET /api/admin/users — รายชื่อผู้ใช้ทั้งหมด เรียงตาม id"""
    error = admin_error()
    if error is not None:
        return error

    users = User.query.order_by(User.id).all()
    items = []
    for user in users:
        items.append(user_to_dict(user))
    return jsonify({"items": items}), 200


@admin_bp.route(f"/users/<{ID}:user_id>", methods=["PATCH"])
def update_user(user_id):
    """PATCH /api/admin/users/<id> — แก้เฉพาะฟิลด์ที่ส่งมา

    ส่งได้ 3 ฟิลด์: displayName, email, password
    ฟิลด์ที่ไม่ส่งมาจะไม่ถูกแตะ กติกาของแต่ละฟิลด์เหมือนตอนสมัครสมาชิก
    """
    error = admin_error()
    if error is not None:
        return error

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "คำขอต้องเป็น JSON object / Request must be a JSON object"}), 400

    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "ไม่พบผู้ใช้ / User not found"}), 404

    if "displayName" in data:
        display_name = data["displayName"]
        if not isinstance(display_name, str) or not display_name.strip():
            return _invalid("displayName", "กรุณาระบุชื่อแสดงผล / displayName required")
        display_name = display_name.strip()
        if len(display_name) > 80:
            return _invalid("displayName", "ชื่อแสดงผลยาวได้ไม่เกิน 80 ตัวอักษร / displayName must be at most 80 characters")
        user.username = display_name

    if "email" in data:
        email = data["email"]
        if not isinstance(email, str) or "@" not in email:
            return _invalid("email", "กรุณาระบุอีเมลที่ถูกต้อง / Valid email required")
        email = email.strip().lower()
        if len(email) > 255:
            return _invalid("email", "อีเมลยาวได้ไม่เกิน 255 ตัวอักษร / email must be at most 255 characters")
        user.email = email

    if "password" in data:
        password = data["password"]
        if not isinstance(password, str) or len(password) < 8:
            return _invalid("password", "รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร / Password must be at least 8 chars")
        # เก็บเป็น hash เหมือนตอนสมัคร — รหัสจริงไม่ถูกเก็บที่ไหนเลย
        user.password_hash = generate_password_hash(password)

    try:
        db.session.commit()
    except IntegrityError:
        # ชื่อหรืออีเมลใหม่ไปซ้ำกับบัญชีอื่น — UNIQUE ในฐานข้อมูลเป็นคนปฏิเสธ
        # rollback เพื่อทิ้งค่าที่แก้ค้างไว้ทั้งหมด ไม่ให้บันทึกครึ่งเดียว
        db.session.rollback()
        return jsonify({"error": _ALREADY_TAKEN}), 400

    return jsonify({"status": "success", "user": user_to_dict(user)}), 200
