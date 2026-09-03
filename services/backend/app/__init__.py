"""
LUMA Backend Application Package
Application Factory `create_app()`
Issue #51 — ระบบความปลอดภัย Security Headers, Cookie Hardening, และ CORS
"""

import os
from datetime import timedelta
from flask import Flask, jsonify, request
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

    # กำหนดค่าเริ่มต้นตามมาตรฐานความปลอดภัย (OWASP & ADR-001)
    app.config.from_mapping(
        SECRET_KEY="luma-dev-secret-key-change-in-production",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(instance_path, 'luma.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        AI_ENGINE_URL="http://127.0.0.1:7860",
        FORGE_TIMEOUT_SECONDS=120,
        # Cookie Hardening ป้องกันการขโมย Cookie ข้ามไซต์
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
    )

    # โหลด config จาก instance/config.py ถ้ามี
    try:
        app.config.from_pyfile("config.py", silent=True)
    except Exception:
        pass

    # Override config สำหรับการรัน test
    if config_overrides:
        app.config.update(config_overrides)

    # สร้างโฟลเดอร์ instance และ upload directory ถ้ายังไม่มี
    os.makedirs(instance_path, exist_ok=True)
    uploads_dir = os.path.join(instance_path, "uploads", "generated")
    os.makedirs(uploads_dir, exist_ok=True)

    # ผูกฐานข้อมูล
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ตั้งค่า CORS และ Security Headers สำหรับทุก response
    @app.after_request
    def apply_security_headers_and_cors(response):
        # 1. CORS Headers
        origin = request.headers.get("Origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-CSRF-Token"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

        # 2. Security Headers (Issue #51 — OWASP Security Standard)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob: http: https:; "
            "connect-src 'self' http://127.0.0.1:* http://localhost:* ws://127.0.0.1:* ws://localhost:*"
        )

        return response

    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            origin = request.headers.get("Origin")
            if origin:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-CSRF-Token"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            return response

    # ลงทะเบียน Error Handlers (ตอบ JSON เสมอ)
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

    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({"error": "พยายามเข้าสู่ระบบบ่อยเกินไป กรุณารอสักครู่ / Too many requests (Rate limit exceeded)"}), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"error": "เกิดข้อผิดพลาดภายในระบบ / Internal server error"}), 500

    # ลงทะเบียน Blueprints
    from app.routes.api import api_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    # Route ตรวจสอบสถานะ Server
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok", "service": "luma-backend"}), 200

    return app
