"""
run.py — Entry Point สำหรับ LUMA Web App
=========================================
รันด้วยคำสั่ง:
    python run.py

เทียบเท่ากับ:
    flask --app app:create_app run

ในโหมด debug จะ reload อัตโนมัติเมื่อแก้ไขโค้ด (Werkzeug reloader)
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True → auto-reload + แสดง error traceback ใน browser
    # ห้ามใช้ debug=True ใน production!
    app.run(debug=True, host="0.0.0.0", port=5000)
