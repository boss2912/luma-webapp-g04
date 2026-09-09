"""
LUMA Backend Application Package
Application Factory `create_app()`
Issue #48 — ระบบ Logging สะอาด ไม่พิมพ์ซ้ำซ้อน
"""

import os
import logging
from flask import Flask, jsonify
from flask_migrate import Migrate
from app.models import db


def setup_logging(app: Flask):
    """
    ตั้งค่าระบบ Logging ไม่ให้พิมพ์ซ้ำซ้อน (Issue #48)
    เมื่อรัน pytest หรือเรียก create_app() ซ้ำหลายครั้ง Handler จะไม่ถูกผูกเบิ้ล
    """
    app.logger.handlers.clear()
    app.logger.propagate = False

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)

    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)


def create_app(config_overrides: dict | None = None) -> Flask:
    """Application Factory สำหรับสร้าง Flask Application พร้อมระบบ Clean Logging"""
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

    # ตั้งค่าระบบ Logging สะอาดไม่ซ้อน (Issue #48)
    setup_logging(app)

    os.makedirs(instance_path, exist_ok=True)

    # ผูกระบบฐานข้อมูลและ Flask-Migrate ตาม ADR-008
    db.init_app(app)

    migrations_dir = os.path.abspath(os.path.join(backend_dir, "..", "database", "migrations"))
    migrate = Migrate(app, db, directory=migrations_dir)

    @app.route("/health", methods=["GET"])
    def health_check():
        app.logger.info("Health check endpoint ถูกเรียกใช้งาน")
        return jsonify({"status": "ok", "service": "luma-backend"}), 200

    return app
