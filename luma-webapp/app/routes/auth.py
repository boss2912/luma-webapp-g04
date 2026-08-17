"""
Auth Blueprint
--------------
Input   : ฟอร์ม username/email/password จากผู้ใช้
Process : ตรวจสอบ / hash password / สร้าง session ผ่าน Flask-Login
Output  : redirect ไปหน้า main, หรือแสดง error รายฟิลด์ใต้ input ถ้าไม่ผ่าน
"""

from collections import defaultdict
from time import time
from urllib.parse import urlparse

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

auth_bp = Blueprint("auth", __name__)

# Fix F14: in-memory rate limiter สำหรับ login (ไม่เพิ่ม dependency ใหม่)
# หมายเหตุ: เก็บใน memory ของ process เดียว ถ้า deploy หลาย worker/process
# แต่ละตัวจะนับแยกกัน — พอสำหรับ dev/งานกลุ่มนี้ ถ้า scale ขึ้นควรย้ายไป Redis
_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_ATTEMPTS = 5
_login_attempts = defaultdict(list)


def _is_rate_limited(key: str) -> bool:
    now = time()
    attempts = _login_attempts[key]
    attempts[:] = [t for t in attempts if now - t < _RATE_LIMIT_WINDOW_SECONDS]
    return len(attempts) >= _RATE_LIMIT_MAX_ATTEMPTS


def _record_failed_attempt(key: str) -> None:
    _login_attempts[key].append(time())


def _is_safe_next_url(target: str | None) -> bool:
    """
    Fix F01: เช็คว่า ?next= เป็น relative path ภายในเว็บนี้เท่านั้น ก่อนอนุญาตให้ redirect
    ปลอดภัย  : "/dashboard", "/api/assets"
    อันตราย  : "https://evil.example", "//evil.example" (protocol-relative)
    """
    if not target:
        return False
    parsed = urlparse(target)
    return not parsed.scheme and not parsed.netloc


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # ถ้า login แล้ว ให้ redirect ไป dashboard เลย
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    errors = {}
    username = email = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username:
            errors["username"] = "กรุณากรอกชื่อผู้ใช้ / Username is required"
        if not email:
            errors["email"] = "กรุณากรอกอีเมล / Email is required"
        # Fix F08: password policy ฝั่ง server (เดิมไม่เช็คความยาวเลย)
        if not password or len(password) < 8:
            errors["password"] = "รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร / Password must be at least 8 characters"

        if not errors:
            # Fix F07 + F12: เช็คซ้ำแบบไม่สนตัวพิมพ์ใหญ่-เล็ก และรวมข้อความ
            # username ซ้ำ / email ซ้ำ เป็นข้อความเดียวกัน กัน account enumeration
            # (ถ้าแยกข้อความ ผู้โจมตีจะรู้ได้ว่า username หรือ email ไหนมีอยู่จริงในระบบ)
            username_taken = User.query.filter(db.func.lower(User.username) == username.lower()).first()
            email_taken = User.query.filter(db.func.lower(User.email) == email).first()
            if username_taken or email_taken:
                errors["general"] = "ไม่สามารถสมัครด้วยข้อมูลนี้ได้ / Unable to register with this information"

        if not errors:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            logger.info(f"[register] new user: {username} ({email})")
            flash("สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ / Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", errors=errors, username=username, email=email)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # ถ้า login แล้ว ให้ redirect ไป dashboard เลย
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    errors = {}

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # key ด้วย email ที่พยายาม login ไม่ใช่ IP — ถ้า key ด้วย IP คนที่ใช้
        # network เดียวกัน (เช่น network มหาลัย/office) จะโดนบล็อกไปด้วยทั้งที่
        # ไม่เกี่ยวกับ account ที่ถูกโจมตี การ key ด้วย email จำกัดผลกระทบไว้แค่
        # account เป้าหมายเท่านั้น
        rate_limit_key = email or (request.remote_addr or "unknown")

        if _is_rate_limited(rate_limit_key):
            errors["general"] = (
                "พยายามเข้าสู่ระบบผิดหลายครั้งเกินไป กรุณารอสักครู่แล้วลองใหม่ / "
                "Too many failed attempts, please wait a moment"
            )
            return render_template("auth/login.html", errors=errors), 429

        user = User.query.filter(db.func.lower(User.email) == email).first()

        if user and user.check_password(password):
            login_user(user)
            logger.info(f"[login] user={user.username} logged in")
            # Fix F01: ยอม redirect เฉพาะ next ที่เป็น path ภายในเว็บนี้เท่านั้น
            next_page = request.args.get("next")
            if not _is_safe_next_url(next_page):
                next_page = None
            return redirect(next_page or url_for("main.dashboard"))

        _record_failed_attempt(rate_limit_key)
        logger.warning(f"[login] failed attempt for email={email}")
        errors["general"] = "อีเมลหรือรหัสผ่านไม่ถูกต้อง / Invalid email or password"

    return render_template("auth/login.html", errors=errors)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    # Fix F15: เปลี่ยนจาก GET เป็น POST-only (GET request ไม่ควรมี side effect
    # เช่นโดน prefetch/crawler ยิงแล้ว logout ผู้ใช้โดยไม่ตั้งใจ)
    logout_user()
    return redirect(url_for("main.index"))
