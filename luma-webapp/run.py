"""
run.py — Entry Point สำหรับ LUMA Web App
=========================================
รันด้วยคำสั่ง:
    python run.py

เทียบเท่ากับ:
    flask --app app:create_app run

ในโหมด debug จะ reload อัตโนมัติเมื่อแก้ไขโค้ด (Werkzeug reloader)

ควบคุมผ่าน environment variable (default = ปลอดภัยที่สุด):
    LUMA_DEBUG=1              เปิด debug mode (ห้ามเปิดพร้อม LUMA_HOST=0.0.0.0)
    LUMA_HOST=0.0.0.0         bind ทุก interface เพื่อให้เครื่องอื่นบน LAN เข้าถึงได้
                              (เช่น ต่อกับเครื่อง Forge AI จริง)
"""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Fix F02: เดิม hardcode debug=True + host="0.0.0.0" เปิด Werkzeug debugger
    # (รันโค้ด Python จากหน้าเว็บได้) ให้ทั้ง network เห็นโดยไม่มีรหัสผ่านป้องกัน
    # ตอนนี้ default คือปิด debug + bind แค่ localhost เท่านั้น
    debug = os.environ.get("LUMA_DEBUG", "0") == "1"
    host = os.environ.get("LUMA_HOST", "127.0.0.1")

    if debug and host == "0.0.0.0":
        # เตือนไว้เผื่อ dev ตั้งค่าผิดโดยไม่ตั้งใจ — ไม่ block เพราะยังมีเคสตั้งใจทำจริง
        print(
            "⚠️  คำเตือน: เปิด LUMA_DEBUG พร้อม LUMA_HOST=0.0.0.0 — "
            "ทุกเครื่องบน network จะเข้าถึง Python debugger ได้ ไม่แนะนำ"
        )

    app.run(debug=debug, host=host, port=5000)
