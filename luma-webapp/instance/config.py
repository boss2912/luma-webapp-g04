# instance/config.py
# ไฟล์นี้เก็บค่าลับของแต่ละเครื่อง -> ต้องอยู่ใน .gitignore ห้าม push ขึ้น GitHub

SECRET_KEY = "change-this-to-a-random-secret-key"

# เริ่มต้นด้วย SQLite เพื่อทดสอบง่าย ๆ ก่อน (ไฟล์เดียว ไม่ต้องติดตั้งอะไรเพิ่ม)
SQLALCHEMY_DATABASE_URI = "sqlite:///luma.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Forge AI endpoint — ชี้ไปที่เครื่องที่รัน Stable Diffusion WebUI (Forge)
# เปลี่ยน localhost เป็น IP เครื่องคนที่ 3 ถ้า deploy บน network เดียวกัน
FORGE_AI_ENDPOINT = "http://localhost:7860/sdapi/v1/txt2img"

# ถ้าจะย้ายไป PostgreSQL ทีหลัง (ดูภาพ Distributed System แบบ 4 เครื่อง) ให้เปลี่ยนเป็น:
# SQLALCHEMY_DATABASE_URI = "postgresql://user:password@host:5432/luma"

