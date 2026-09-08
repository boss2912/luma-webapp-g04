"""
LUMA Backend Application Package
Application Factory `create_app()`
Issue #51 — OWASP Security Headers, Cookie Hardening & Rate Limiting
"""

import os
from flask import Flask, jsonify, request
from app.models import db


def create_app(config_overrides: dict | None = None) -> Flask:
    """Application Factory สำหรับสร้าง Flask Application พร้อมเกราะความปลอดภัย OWASP"""
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
        # Cookie Hardening (Issue #51)
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    try:
        app.config.from_pyfile("config.py", silent=True)
    except Exception:
        pass

    if config_overrides:
        app.config.update(config_overrides)

    os.makedirs(instance_path, exist_ok=True)

    db.init_app(app)

    with app.app_context():
        db.create_all()

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

    # 429 Too Many Requests Error Handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({"error": "คำขอถี่เกินกำหนด กรุณารอสักครู่ / Too many requests"}), 429

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok", "service": "luma-backend"}), 200

    return app
