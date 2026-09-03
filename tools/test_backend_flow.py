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
"""

import os
import sys
import importlib

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "services", "backend")
TESTS_DIR = os.path.join(BACKEND_DIR, "tests")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)


def main():
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    files_to_run = []
    if target in ("all", "health"):
        files_to_run.append(("test_health.py", "test_health"))
    if target in ("all", "auth"):
        files_to_run.append(("test_auth.py", "test_auth"))
    if target in ("all", "generate"):
        files_to_run.append(("test_generate.py", "test_generate"))
    if target in ("all", "assets"):
        files_to_run.append(("test_assets.py", "test_assets"))

    if not files_to_run:
        print(f"❌ ไม่พบกลุ่มการทดสอบ '{target}' — เลือกได้: health, auth, generate, assets, all")
        sys.exit(1)

    print("=" * 65)
    print("🧪 กำลังเริ่มต้นทดสอบระบบ Flask Backend API (LUMA)")
    print("=" * 65)

    for filename, modname in files_to_run:
        filepath = os.path.join(TESTS_DIR, filename)
        if os.path.exists(filepath):
            # รันไฟล์ทดสอบโดยตรง
            os.system(f'"{sys.executable}" "{filepath}"')


if __name__ == "__main__":
    main()
