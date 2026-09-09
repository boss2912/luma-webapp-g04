"""
LUMA Backend Application Package
Application Factory `create_app()`
Issue #46 — create_app() + ระบบจัดการ Config อย่างปลอดภัย
Issue #51 — OWASP Security Headers, Cookie Hardening & Rate Limiting
"""

import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from app.models import db


def create_app(config_overrides: dict | None = None) -> Flask:
    """
    Application Factory สำหรับสร้าง Flask Application
    - กำหนด instance_path ไปที่ services/backend/instance/
    - โหลด config พื้นฐาน และโหลด config.py จาก instance/
    - ผูกระบบฐานข้อมูลและ Flask-Migrate ตาม ADR-008
    - รองรับ config_overrides สำหรับการรันแบบทดสอบ
    - แนบ Security Headers (OWASP) และ Cookie Hardening ในทุก Response (Issue #51)
    """
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    instance_path = os.path.join(backend_dir, "instance")

    app = Flask(
        __name__,
        instance_path=instance_path,
        instance_relative_config=True,
    )

    # 1. กำหนดค่าคอนฟิกเริ่มต้น (Default Configurations)
    app.config.from_mapping(
        SECRET_KEY="luma-dev-secret-key-change-in-production",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(instance_path, 'luma.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        AI_ENGINE_URL="http://127.0.0.1:7860",
        FORGE_TIMEOUT_SECONDS=120,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    # 2. โหลดค่าคอนฟิกจาก instance/config.py (ถ้ามี)
    try:
        app.config.from_pyfile("config.py", silent=True)
    except Exception:
        pass

    # 3. นำค่า config_overrides มาทับสำหรับการรันเทส (Testing Mode)
    if config_overrides:
        app.config.update(config_overrides)

    # 4. สร้างโฟลเดอร์ instance และ upload directory ถ้ายังไม่มี
    os.makedirs(instance_path, exist_ok=True)
    uploads_dir = os.path.join(instance_path, "uploads", "generated")
    os.makedirs(uploads_dir, exist_ok=True)

    # 5. ผูกระบบฐานข้อมูล SQLAlchemy และ Flask-Migrate ตาม ADR-008
    db.init_app(app)

    migrations_dir = os.path.abspath(os.path.join(backend_dir, "..", "database", "migrations"))
    migrate = Migrate(app, db, directory=migrations_dir)

    # ==========================================================================
    # Security Headers (OWASP) แนบในทุก Response (Issue #51)
    # ==========================================================================
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: http: https:; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline';"
        )
        return response

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({"error": "คำขอถี่เกินกำหนด กรุณารอสักครู่ / Too many requests"}), 429

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Route ตรวจสอบสถานะ Server
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok", "service": "luma-backend"}), 200

    return app
