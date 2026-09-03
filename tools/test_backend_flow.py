#!/usr/bin/env python3
"""
tools/test_backend_flow.py — สคริปต์ทดสอบระบบ Backend แบบสรุปผลภาษาไทย
======================================================================
การใช้งาน:
    python tools/test_backend_flow.py           # รันทุกเรื่องพร้อมกัน
    python tools/test_backend_flow.py health    # รันเฉพาะ health
    python tools/test_backend_flow.py auth      # รันเฉพาะ auth
    python tools/test_backend_flow.py generate  # รันเฉพาะ generate
    python tools/test_backend_flow.py assets    # รันเฉพาะ assets
    python tools/test_backend_flow.py security  # รันเฉพาะ security
    python tools/test_backend_flow.py logging   # รันเฉพาะ logging
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "services", "backend")
TESTS_DIR = os.path.join(BACKEND_DIR, "tests")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)


def main():
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    all_files = [
        ("test_health.py", "สถานะเซิร์ฟเวอร์ (Health Check)"),
        ("test_auth.py", "ระบบสมาชิก (Authentication Flow)"),
        ("test_generate.py", "ระบบสร้างภาพ AI (Generate Image)"),
        ("test_assets.py", "ระบบคลังผลงาน (Asset Gallery & Search)"),
        ("test_security.py", "ความปลอดภัยตามมาตรฐาน OWASP (Security & Rate Limit)"),
        ("test_logging.py", "ระบบบันทึก Log สะอาดไม่ซ้อน (Clean Logging)"),
    ]

    files_to_run = []
    if target == "all":
        files_to_run = all_files
    else:
        for filename, desc in all_files:
            if target in filename:
                files_to_run.append((filename, desc))

    if not files_to_run:
        print(f"❌ ไม่พบกลุ่มการทดสอบ '{target}' — เลือกได้: health, auth, generate, assets, security, logging, all")
        sys.exit(1)

    print("=" * 65)
    print("🧪 กำลังเริ่มต้นทดสอบระบบ Flask Backend API (LUMA)")
    print("=" * 65)

    for filename, desc in files_to_run:
        filepath = os.path.join(TESTS_DIR, filename)
        if os.path.exists(filepath):
            os.system(f'"{sys.executable}" "{filepath}"')


if __name__ == "__main__":
    main()
