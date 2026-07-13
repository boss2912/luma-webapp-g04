"""
Auth Blueprint
--------------
Input   : ฟอร์ม username/email/password จากผู้ใช้
Process : ตรวจสอบ / hash password / สร้าง session ผ่าน Flask-Login
Output  : redirect ไปหน้า main, หรือแสดง error ถ้า login ไม่ผ่าน
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("อีเมลนี้ถูกใช้แล้ว")
            return redirect(url_for("auth.register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.dashboard"))

        flash("อีเมลหรือรหัสผ่านไม่ถูกต้อง")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
