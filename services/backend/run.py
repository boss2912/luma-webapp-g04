"""
LUMA Backend Server Runner
Entry point สำหรับสั่งรัน Development Server
"""

import os
import sys

# เพิ่มโฟลเดอร์ services/backend เข้า sys.path เพื่อให้ import app ได้ถูกต้อง
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"🚀 LUMA Backend Server กำลังทำงานที่ http://127.0.0.1:{port}")
    app.run(host=host, port=port, debug=True)
