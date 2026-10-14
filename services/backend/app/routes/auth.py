"""
LUMA Auth Routes
Endpoints สำหรับระบบสมาชิก Authentication พร้อมระบบ Rate Limiting (Issue #50/#51)
"""

import hashlib
import time
from flask import Blueprint, jsonify, request, session, current_app
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User, db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# ระบบบันทึกการพยายาม Login ล้มเหลวแบบ In-memory (อีเมล -> [timestamp1, timestamp2, ...])
#
# นับตามอีเมลที่พยายามล็อกอิน ไม่ใช่ IP (#15 F14): คนใช้ network เดียวกัน (Wi-Fi มหาลัย, NAT)
# มี IP ขาออกเดียวกัน นับตาม IP แล้วคนเดียวเดารหัสผิดทำให้ทุกคนล็อกอินไม่ได้ ส่วนคนร้าย
# สลับ IP ได้ง่ายกว่าสลับบัญชีเป้าหมาย
#
# ข้อจำกัดที่รู้อยู่: dict นี้อยู่ในโปรเซสเดียว — รีสตาร์ทแอปแล้วรีเซ็ตทันที
# และถ้ารันหลาย worker/instance พร้อมกัน แต่ละตัวจะนับแยกกันเอง (ไม่ share state)
# พอใช้สำหรับเดโม/รันเครื่องเดียว แต่ deploy จริงหลายเครื่องต้องย้ายไป Redis (V5, F14)
# หรือที่เก็บกลางแบบอื่นถึงจะกันการเดารหัสผ่านได้จริง
_login_failed_attempts: dict[str, list[float]] = {}

# ข้อความ error เดียวกันทั้งสองกรณี (ไม่มี user / รหัสผิด) กันคนเดา
# ว่าอีเมลไหนสมัครไว้แล้วจากข้อความ error ที่ต่างกัน
_INVALID_CREDENTIALS = "ชื่อ/อีเมล หรือรหัสผ่านไม่ถูกต้อง / Invalid credentials"

# สมัครซ้ำ: ข้อความเดียวไม่ว่าจะซ้ำที่อีเมลหรือชื่อ และตอบ 400 ตาม docs/API_CONTRACT.md (#49)
_ALREADY_TAKEN = "อีเมลหรือชื่อนี้ถูกใช้แล้ว / Email or displayName already taken"


def _invalid(field: str, message: str):
    """400 ที่บอกว่าฟิลด์ไหนผิด — `errors` ตาม contract ส่วน `error` ให้ register.js ที่อ่านอยู่แล้ว"""
    return jsonify({"error": message, "errors": {field: message}}), 400


def check_rate_limit(key: str, max_attempts: int = 5, window_seconds: int = 60) -> bool:
    """ตรวจสอบว่าบัญชีนี้ (key = อีเมลแบบ lower) ถูกบล็อกจาก Rate Limiting หรือไม่"""
    now = time.time()

    # ล้าง key ที่ timestamps หมดอายุทั้งหมดออกจาก dict เพื่อป้องกัน memory leak จากอีเมลสุ่ม (#212)
    expired_keys = [
        k for k, timestamps in list(_login_failed_attempts.items())
        if not any(now - t < window_seconds for t in timestamps)
    ]
    for k in expired_keys:
        _login_failed_attempts.pop(k, None)

    attempts = _login_failed_attempts.get(key)
    if not attempts:
        return False

    # ลบ timestamps ที่หมดอายุเกิน window_seconds ออก
    valid_attempts = [t for t in attempts if now - t < window_seconds]
    if not valid_attempts:
        _login_failed_attempts.pop(key, None)
        return False

    _login_failed_attempts[key] = valid_attempts
    return len(valid_attempts) >= max_attempts


def record_failed_attempt(key: str):
    """บันทึกการพยายาม Login ที่ล้มเหลว

    ใช้ setdefault ทำเช็ค+สร้าง list ในจังหวะเดียว (atomic) — ถ้าแยกเป็น
    "เช็คว่ามี key ไหม" แล้ว "append" คนละบรรทัด คำขออื่นที่ sweep dict
    (บรรทัด 46-51) แทรกกลางได้ ลบ key ทิ้งก่อน append จะชน KeyError (#224 review)
    """
    _login_failed_attempts.setdefault(key, []).append(time.time())


def reset_rate_limit(key: str):
    """ล้างประวัติการพยายามเมื่อ Login สำเร็จ"""
    _login_failed_attempts.pop(key, None)


def password_stamp(user) -> str:
    """ตราประจำรหัสผ่านของผู้ใช้ — เปลี่ยนทุกครั้งที่ password_hash เปลี่ยน

    ตอนล็อกอินเก็บตรานี้ลง session แล้วทุกคำขอเอามาเทียบกับค่าในฐานข้อมูล
    ถ้า admin ตั้งรหัสใหม่ ตราในฐานข้อมูลจะเปลี่ยน session เก่าจึงเทียบไม่ตรงและใช้ไม่ได้

    ใช้ sha256 ของ password_hash อีกชั้น ไม่เก็บท่อนของ password_hash ตรงๆ
    เพราะ cookie ของ session อ่านได้ที่เครื่องผู้ใช้ (แค่เซ็นชื่อกันแก้ ไม่ได้เข้ารหัส)
    """
    return hashlib.sha256(user.password_hash.encode("utf-8")).hexdigest()[:16]


@auth_bp.before_app_request
def drop_session_after_password_change():
    """รันก่อนทุกคำขอของทั้งแอป — เตะ session ที่ล็อกอินไว้ก่อนรหัสผ่านถูกเปลี่ยน

    ลบ user_id ออกจาก session แล้วปล่อยให้คำขอเดินต่อ
    route ทุกตัวเช็ค session.get("user_id") อยู่แล้ว จึงตอบ 401 เองโดยไม่ต้องแก้ทีละ route

    ข้อจำกัด: session ที่ไม่มี pw_stamp (cookie ที่ออกก่อนมีระบบนี้) จะไม่ถูกเช็ค
    ล็อกอินครั้งถัดไปถึงจะได้ตรา ถ้าต้องการเตะ cookie เก่าทั้งหมดตอนอัปเดต ให้เปลี่ยน SECRET_KEY
    """
    user_id = session.get("user_id")
    stamp = session.get("pw_stamp")
    if not user_id or stamp is None:
        return None

    user = db.session.get(User, user_id)
    if user is not None and stamp != password_stamp(user):
        session.pop("user_id", None)
        session.pop("pw_stamp", None)
    return None


@auth_bp.route("/ping", methods=["GET"])
def ping():
    """GET /api/auth/ping — ตรวจสอบการทำงานของ Blueprint auth (Issue #47)"""
    return jsonify({"status": "ok", "blueprint": "auth"}), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    """POST /api/auth/register — สมัครสมาชิกใหม่ บันทึกลงตาราง users จริง (Issue #16/#50)"""
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "คำขอต้องเป็น JSON object / Request must be a JSON object"}), 400
    email = data.get("email", "")
    display_name = data.get("displayName", "")
    password = data.get("password", "")
    if not all(isinstance(v, str) for v in (email, display_name, password)):
        return jsonify({"error": "email, displayName, password ต้องเป็นข้อความ / must be strings"}), 400
    email = email.strip().lower()
    display_name = display_name.strip()

    if not email or "@" not in email:
        return _invalid("email", "กรุณาระบุอีเมลที่ถูกต้อง / Valid email required")
    if not display_name:
        return _invalid("displayName", "กรุณาระบุชื่อแสดงผล / displayName required")
    # ความยาวตาม schema (users.username String(80) · users.email String(255))
    # SQLite ไม่บังคับความยาวเอง — ไม่ตรวจที่นี่ ชื่อยาว 1 MB ก็เก็บลงฐานได้ (fuzz #207)
    if len(display_name) > 80:
        return _invalid("displayName", "ชื่อแสดงผลยาวได้ไม่เกิน 80 ตัวอักษร / displayName must be at most 80 characters")
    if len(email) > 255:
        return _invalid("email", "อีเมลยาวได้ไม่เกิน 255 ตัวอักษร / email must be at most 255 characters")
    # โดเมนต้องอยู่ใน ALLOWED_EMAIL_DOMAINS (ค่าเริ่มต้นอยู่ใน create_app) · None = รับทุกโดเมน
    allowed_domains = current_app.config["ALLOWED_EMAIL_DOMAINS"]
    email_domain = email.rsplit("@", 1)[1]
    if allowed_domains and email_domain not in allowed_domains:
        domain_list = ", ".join("@" + domain for domain in allowed_domains)
        return _invalid("email", f"สมัครได้เฉพาะอีเมล {domain_list} / Only {domain_list} emails can register")
    if not password or len(password) < 8:
        return _invalid("password", "รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร / Password must be at least 8 chars")

    # ชื่อเทียบแบบไม่สนตัวพิมพ์เหมือนอีเมล ("Aaa" กับ "aaa" คือคนเดียวกัน) แต่เก็บตามที่ผู้ใช้พิมพ์
    existing = User.query.filter(
        (User.email == email) | (func.lower(User.username) == display_name.lower())
    ).first()
    if existing is not None:
        return jsonify({"error": _ALREADY_TAKEN}), 400

    user = User(
        username=display_name,
        email=email,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        # สองคนสมัครพร้อมกันผ่านด่านเช็คข้างบนไปทั้งคู่ -> UNIQUE ในฐานปฏิเสธคนที่สอง
        db.session.rollback()
        return jsonify({"error": _ALREADY_TAKEN}), 400

    return jsonify({
        "status": "success",
        "message": "สมัครสมาชิกสำเร็จ",
        "user": {"email": user.email, "displayName": user.username},
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """POST /api/auth/login — เข้าสู่ระบบด้วยข้อมูลจริงจากตาราง users พร้อม Rate Limiting (Issue #50/#51)"""
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "คำขอต้องเป็น JSON object / Request must be a JSON object"}), 400
    # ช่องเดียวรับได้ทั้งชื่อและอีเมล — หน้าเว็บส่งมาในคีย์ "login"
    # ถ้าไม่มีคีย์ "login" ให้อ่านคีย์ "email" แทน ของเดิมที่ส่งอีเมลมาจึงยังใช้ได้
    login_name = data.get("login", data.get("email", ""))
    password = data.get("password", "")
    if not isinstance(login_name, str) or not isinstance(password, str):
        return jsonify({"error": "login และ password ต้องเป็นข้อความ / must be strings"}), 400
    login_name = login_name.strip()

    if not login_name or not password:
        return jsonify({"error": "กรุณาระบุชื่อหรืออีเมล และรหัสผ่าน / Login and password required"}), 400

    # มี @ = ค้นจากอีเมล · ไม่มี @ = ค้นจากชื่อ (ค้นทีละคอลัมน์ ไม่ค้นสองคอลัมน์พร้อมกัน)
    # เหตุผล: หน้าสมัครยอมให้ตั้งชื่อที่มี @ ได้ ถ้าค้นสองคอลัมน์พร้อมกัน
    # คนที่ตั้งชื่อตัวเองเป็นอีเมลของคนอื่นจะถูกหยิบขึ้นมาแทนเจ้าของอีเมลได้
    # คอลัมน์ทั้งสองเป็น COLLATE NOCASE อยู่แล้ว จึงไม่สนตัวพิมพ์เล็กใหญ่
    if "@" in login_name:
        user = User.query.filter_by(email=login_name.lower()).first()
    else:
        user = User.query.filter_by(username=login_name).first()

    # นับการเดารหัสผิด "ต่อบัญชี" — ถ้าเจอบัญชี ใช้อีเมลของบัญชีนั้นเป็นตัวนับ
    # ไม่งั้นคนเดาจะสลับพิมพ์ชื่อกับอีเมลของบัญชีเดียวกัน แล้วได้จำนวนครั้งเป็นสองเท่า
    if user is not None:
        rate_key = user.email
    else:
        rate_key = login_name.lower()

    # 1. ตรวจสอบ Rate Limiting ต่อบัญชี (บล็อกถ้าผิดเกิน 5 ครั้งใน 1 นาที) — เช็คก่อนเทียบรหัส
    #    ทำให้ช่วงที่โดนบล็อก รหัสถูกก็เข้าไม่ได้ คนเดาจึงแยกไม่ออกว่าเดาถูกแล้วหรือยัง
    # ค่า default ตั้งได้ผ่าน instance/config.py (#192) — .get() ใส่ 5/60 เดิมไว้เป็น
    # fallback เพื่อไม่ให้เครื่องที่ยังไม่ copy config.py มามีพฤติกรรมเปลี่ยน
    if check_rate_limit(
        rate_key,
        max_attempts=current_app.config.get("RATE_LIMIT_MAX_ATTEMPTS", 5),
        window_seconds=current_app.config.get("RATE_LIMIT_WINDOW_SECONDS", 60),
    ):
        # log แค่ IP ไม่ log อีเมลที่พยายาม (ข้อมูลส่วนบุคคล)
        current_app.logger.warning("Rate limit exceeded (login) จาก IP: %s", request.remote_addr)
        return jsonify({
            "error": "พยายามเข้าสู่ระบบผิดพลาดเกินกำหนด กรุณารอ 1 นาที / Too many login attempts. Please try again in 1 minute.",
        }), 429

    # 2. เทียบรหัสผ่านจริงกับ hash ในตาราง users — ไม่ใช่การเทียบสตริง/ความยาวแบบเดิม
    if user is None or not check_password_hash(user.password_hash, password):
        record_failed_attempt(rate_key)
        return jsonify({"error": _INVALID_CREDENTIALS}), 401

    # Login สำเร็จ -> ล้างประวัติล้มเหลว
    reset_rate_limit(rate_key)

    # เก็บแค่ user_id ใน session ไม่ยัดข้อมูล user ทั้งก้อนลง cookie
    session["user_id"] = user.id
    # ตราของรหัสผ่านตอนล็อกอิน — ใช้เตะ session นี้เมื่อรหัสถูกเปลี่ยนทีหลัง
    session["pw_stamp"] = password_stamp(user)

    return jsonify({
        "status": "success",
        "message": "เข้าสู่ระบบสำเร็จ",
        "user": {"email": user.email, "displayName": user.username, "role": user.role},
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """POST /api/auth/logout — ออกจากระบบและล้าง Session (Issue #50)"""
    session.pop("user_id", None)
    session.pop("pw_stamp", None)
    return jsonify({
        "status": "success",
        "message": "ออกจากระบบสำเร็จ",
    }), 200


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """GET /api/auth/me — ตรวจสอบข้อมูลผู้ใช้ที่ล็อกอินอยู่ (Issue #50)"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "ยังไม่ได้เข้าสู่ระบบ / Unauthorized"}), 401

    user = db.session.get(User, user_id)
    if user is None:
        # user_id ใน session ชี้ไป user ที่ถูกลบไปแล้ว — ถือว่า session ใช้ไม่ได้แล้ว
        session.pop("user_id", None)
        return jsonify({"error": "ยังไม่ได้เข้าสู่ระบบ / Unauthorized"}), 401

    # role ส่งไปให้หน้าเว็บตัดสินว่าจะแสดงเมนู "จัดการผู้ใช้" ไหม
    # (เป็นแค่การซ่อนเมนู การกันจริงอยู่ที่ /api/admin/* ซึ่งเช็ค role ที่ฝั่งนี้อีกรอบ)
    return jsonify({"email": user.email, "displayName": user.username, "role": user.role}), 200
