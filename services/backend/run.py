#!/usr/bin/env python3
"""
LUMA Backend Runner
Entry point สำหรับเริ่มต้นรันเซิร์ฟเวอร์ Flask Backend
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("🚀 LUMA Backend Server กำลังทำงานที่ http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
