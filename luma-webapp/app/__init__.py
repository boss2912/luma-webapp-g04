"""
Application Factory Pattern
----------------------------
Input   : Flask config (จาก instance/config.py)
Process : สร้าง Flask app -> ผูก SQLAlchemy -> ผูก Login Manager -> ลงทะเบียน Blueprint
Output  : app object พร้อมใช้งาน (import ไปใช้ใน run.py)
"""

from flask import Flask, jsonify, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

# --- Extensions (ประกาศไว้นอกฟังก์ชัน เพื่อให้ import ไปใช้ที่อื่นได้ เช่น models.py) ---
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
# Fix F06: เดิมติดตั้ง Flask-WTF ไว้ใน requirements.txt แต่ไม่เคยเปิดใช้ CSRFProtect เลย
# ทำให้ฟอร์ม login/register/logout โดน CSRF attack ได้ (เว็บอื่นสั่งให้ browser
# ยิง POST มาที่เว็บนี้แทนผู้ใช้ได้โดยไม่รู้ตัว)
csrf = CSRFProtect()


def create_app(config_overrides=None):
    app = Flask(__name__, instance_relative_config=True)

    # 1) โหลด config จาก instance/config.py (เก็บ SECRET_KEY, DB URI ที่นี่ ไม่ push ขึ้น git)
    # silent=True: ไฟล์นี้ไม่ถูก track ใน git แล้ว (F09) เครื่องที่เพิ่ง clone หรือ
    # test runner (Issue #6) จะยังไม่มีไฟล์นี้ — ให้ทำงานต่อได้ด้วยค่า default
    # แทนที่จะ crash ตั้งแต่ตอน import
    app.config.from_pyfile("config.py", silent=True)
    app.config.setdefault("SECRET_KEY", "dev-only-insecure-key-set-real-one-in-instance-config-py")
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///luma.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config.setdefault("FORGE_AI_ENDPOINT", "http://localhost:7860/sdapi/v1/txt2img")

    if config_overrides:
        app.config.update(config_overrides)

    # 2) ผูก extensions เข้ากับ app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"

    # Fix F10: เดิม Flask-Login redirect ไปหน้า login (HTML) เสมอเวลาไม่ได้ login
    # แม้จะเป็น /api/* ที่ frontend คาดหวัง JSON ก็ตาม ทำให้ fetch() ฝั่ง JS
    # พยายาม parse HTML เป็น JSON แล้ว error อธิบายไม่ได้ว่าเกิดอะไรขึ้น
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/api/"):
            return jsonify({"error": "unauthorized — กรุณาเข้าสู่ระบบก่อน / please log in"}), 401
        return redirect(url_for("auth.login", next=request.path))

    # 3) ตั้งค่า Logging ผ่าน utils/logger.py (แยก concern ออกจาก factory)
    from app.utils.logger import setup_logging
    setup_logging(app)

    # 4) ลงทะเบียน Blueprint (แยกไฟล์ตามหน้าที่ auth / api / main)
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Fix F06 (ต่อ): ยกเว้น CSRF ให้ /api/* เพราะเป็น JSON endpoint ล้วน ไม่ได้ใช้ฟอร์ม
    # HTML — ป้องกัน CSRF ของ JSON API ด้วยการเช็ค Content-Type แทน (browser ฟอร์มธรรมดา
    # ยิง JSON ตรงๆ ไม่ได้อยู่แล้ว) ส่วนฟอร์ม HTML จริง (login/register/logout) ยังคง
    # บังคับ csrf_token ตามปกติ
    csrf.exempt(api_bp)

    # 5) import models เพื่อให้ SQLAlchemy รู้จักตาราง แล้วสร้างไฟล์ DB ถ้ายังไม่มี
    from app import models
    with app.app_context():
        db.create_all()

    return app

