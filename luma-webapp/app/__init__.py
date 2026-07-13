"""
Application Factory Pattern
----------------------------
Input   : Flask config (จาก instance/config.py)
Process : สร้าง Flask app -> ผูก SQLAlchemy -> ผูก Login Manager -> ลงทะเบียน Blueprint
Output  : app object พร้อมใช้งาน (import ไปใช้ใน run.py)
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# --- Extensions (ประกาศไว้นอกฟังก์ชัน เพื่อให้ import ไปใช้ที่อื่นได้ เช่น models.py) ---
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # 1) โหลด config จาก instance/config.py (เก็บ SECRET_KEY, DB URI ที่นี่ ไม่ push ขึ้น git)
    app.config.from_pyfile("config.py")

    # 2) ผูก extensions เข้ากับ app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = "auth.login"

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

    # 5) import models เพื่อให้ SQLAlchemy รู้จักตาราง แล้วสร้างไฟล์ DB ถ้ายังไม่มี
    from app import models
    with app.app_context():
        db.create_all()

    return app

