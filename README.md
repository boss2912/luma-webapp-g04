# LUMA Web App — Group 04
# โปรเจค Image Processing / AI Image Generation

<div align="center">
  <h1>🎨 LUMA</h1>
  <p><strong>Learning-based Universal Media Artist</strong></p>
  <p>
    เว็บแอปสร้างภาพด้วย AI ผ่าน Stable Diffusion WebUI (Forge) ·
    AI Image Generation Web App powered by Stable Diffusion
  </p>

  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0-green?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/SQLAlchemy-3.1-orange" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/Branch-main-purple" alt="Branch">
</div>

---

## 📖 ภาพรวมโปรเจค / Project Overview

| ภาษาไทย | English |
|---------|---------|
| ระบบเว็บที่ให้ผู้ใช้ล็อกอินแล้ว generate ภาพจาก text prompt | Web system where authenticated users can generate images from text prompts |
| Backend: Flask + SQLAlchemy + Jinja2 | Backend: Flask + SQLAlchemy + Jinja2 |
| AI Engine: Stable Diffusion WebUI Forge (Stability Matrix) | AI Engine: Stable Diffusion WebUI Forge (Stability Matrix) |
| Database: SQLite (dev) / PostgreSQL (production) | Database: SQLite (dev) / PostgreSQL (production) |

---

## 👥 ทีม / Team (Group 04)

| บทบาท / Role | หน้าที่ / Responsibility | Branch |
|------|------|------|
| 🧑‍💻 Backend Lead (หัวหน้า) | Flask, Auth, API, Database | `feature/backend-auth` |
| 🤖 AI Engineer | Forge AI Integration, Job Queue, Testing | `feature/forge-ai` |
| 🎨 UI/Frontend | Jinja2 Templates, CSS, JavaScript | `feature/ui-frontend` |

---

## 🚀 การติดตั้ง / Installation

> ดูรายละเอียดครบถ้วนได้ที่ [INSTALL.md](luma-webapp/INSTALL.md)

### วิธีที่ 1: Conda (แนะนำ / Recommended)
```bash
git clone https://github.com/boss2912/luma-webapp-g04.git
cd luma-webapp-g04/luma-webapp

conda env create -f environment.yml
conda activate luma

python run.py
```

### วิธีที่ 2: pip + venv
```bash
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

### ⚙️ ตั้งค่า Config / Configuration
สร้างไฟล์ `luma-webapp/instance/config.py`:
```python
SECRET_KEY = "your-random-secret-key"
SQLALCHEMY_DATABASE_URI = "sqlite:///luma.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
FORGE_AI_ENDPOINT = "http://localhost:7860/sdapi/v1/txt2img"
```

---

## 📁 โครงสร้างโปรเจค / Project Structure

```
luma-webapp-g04/
└── luma-webapp/
    ├── run.py                  ← รันด้วย: python run.py
    ├── requirements.txt
    ├── environment.yml
    ├── INSTALL.md
    ├── CONTRIBUTING.md         ← กติกา Git สำหรับทีม
    ├── app/
    │   ├── __init__.py         ← create_app() factory
    │   ├── models.py           ← User, Asset, Job
    │   ├── routes/
    │   │   ├── auth.py         ← /auth/*
    │   │   ├── api.py          ← /api/*
    │   │   └── main.py         ← / /dashboard
    │   ├── templates/          ← Jinja2 HTML
    │   ├── static/css/         ← style.css
    │   └── utils/logger.py     ← logging
    └── instance/
        └── config.py           ← ⚠️ ไม่ push ขึ้น git
```

---

## 🌐 API Endpoints

| Method | Path | Auth | คำอธิบาย / Description |
|--------|------|------|----------------------|
| GET | `/` | ไม่ต้อง | หน้าแรก / Home |
| GET | `/dashboard` | ✅ | Dashboard + Generate |
| POST | `/auth/register` | ไม่ต้อง | สมัครสมาชิก / Register |
| POST | `/auth/login` | ไม่ต้อง | เข้าสู่ระบบ / Login |
| GET | `/auth/logout` | ✅ | ออกจากระบบ / Logout |
| POST | `/api/generate` | ✅ | Generate ภาพ / Generate image |
| GET | `/api/assets` | ✅ | ดูรูปทั้งหมด / List assets |

---

## 🌿 Git Workflow

```
main     ────────────────────────● (release เท่านั้น / release only)
                                 ↑
develop  ──●──●──●──●──●──●──●──● (รวมงาน / integration)
           ↑       ↑       ↑
feature/backend-auth  feature/forge-ai  feature/ui-frontend
```

> ดูกติกาการทำงานทั้งหมดได้ที่ [CONTRIBUTING.md](luma-webapp/CONTRIBUTING.md)

---

## 📄 License

MIT License — สำหรับการศึกษา / For educational purposes
