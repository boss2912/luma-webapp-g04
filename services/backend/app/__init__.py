"""
LUMA Backend Application Package
Application Factory `create_app()`
Issue #47 — Blueprint Modular Architecture & JSON Error Handlers
"""

import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from app.models import db


def create_app(config_overrides: dict | None = None) -> Flask:
    """Application Factory สำหรับสร้าง Flask Application พร้อม Blueprint และ JSON Error Handlers"""
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    instance_path = os.path.join(backend_dir, "instance")

    app = Flask(
        __name__,
        instance_path=instance_path,
        instance_relative_config=True,
    )

    app.config.from_mapping(
        SECRET_KEY="luma-dev-secret-key-change-in-production",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(instance_path, 'luma.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    try:
        app.config.from_pyfile("config.py", silent=True)
    except Exception:
        pass

    if config_overrides:
        app.config.update(config_overrides)

    os.makedirs(instance_path, exist_ok=True)

    # ผูกระบบฐานข้อมูลและ Flask-Migrate ตาม ADR-008
    db.init_app(app)

    migrations_dir = os.path.abspath(os.path.join(backend_dir, "..", "database", "migrations"))
    migrate = Migrate(app, db, directory=migrations_dir)

    # ==========================================================================
    # ลงทะเบียน JSON Error Handlers (Issue #47)
    # ==========================================================================
    @app.errorhandler(400)
    def bad_request(error):
        msg = getattr(error, "description", "ข้อมูลไม่ถูกต้อง / Bad request")
        return jsonify({"error": msg}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "ยังไม่ได้เข้าสู่ระบบ / Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"error": "ไม่มีสิทธิ์เข้าถึง / Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "ไม่พบหน้าที่ระบุ / Not found"}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"error": "เกิดข้อผิดพลาดภายในระบบ / Internal server error"}), 500

    # ==========================================================================
    # ลงทะเบียน Blueprints (Issue #47)
    # ==========================================================================
    from app.routes.api import api_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok", "service": "luma-backend"}), 200

    return app
