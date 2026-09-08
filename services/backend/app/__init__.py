"""
LUMA Backend Application Package
Application Factory `create_app()`
Issue #22 — POST /api/generate
"""

import os
from flask import Flask, jsonify
from app.models import db


def create_app(config_overrides: dict | None = None) -> Flask:
    """Application Factory สำหรับสร้าง Flask Application"""
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
        AI_ENGINE_URL="http://127.0.0.1:7860",
        FORGE_TIMEOUT_SECONDS=120,
    )

    try:
        app.config.from_pyfile("config.py", silent=True)
    except Exception:
        pass

    if config_overrides:
        app.config.update(config_overrides)

    os.makedirs(instance_path, exist_ok=True)
    uploads_dir = os.path.join(instance_path, "uploads", "generated")
    os.makedirs(uploads_dir, exist_ok=True)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from app.routes.api import api_bp
    app.register_blueprint(api_bp)

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok", "service": "luma-backend"}), 200

    return app
