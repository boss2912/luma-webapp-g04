"""
Auth Blueprint
--------------
Input   : ฟอร์ม username/email/password จากผู้ใช้
Process : ตรวจสอบ / hash password / สร้าง session ผ่าน Flask-Login
Output  : redirect ไปหน้า main, หรือแสดง error ถ้า login ไม่ผ่าน
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # ถ้า login แล้ว ให้ redirect ไป dashboard เลย
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        # เช็ค username ซ้ำ
        if User.query.filter_by(username=username).first():
            flash("ชื่อผู้ใช้นี้ถูกใช้แล้ว / Username already taken", "error")
            return redirect(url_for("auth.register"))

        # เช็ค email ซ้ำ
        if User.query.filter_by(email=email).first():
            flash("อีเมลนี้ถูกใช้แล้ว / Email already registered", "error")
            return redirect(url_for("auth.register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        logger.info(f"[register] new user: {username} ({email})")
        flash("สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ / Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # ถ้า login แล้ว ให้ redirect ไป dashboard เลย
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            logger.info(f"[login] user={user.username} logged in")
            # redirect ไปหน้าที่ผู้ใช้ต้องการก่อน login (ถ้ามี)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

        logger.warning(f"[login] failed attempt for email={email}")
        flash("อีเมลหรือรหัสผ่านไม่ถูกต้อง / Invalid email or password", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
