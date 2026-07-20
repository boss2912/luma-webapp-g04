# LUMA Web App — Installation Guide

**LUMA** (Learning-based Universal Media Artist) — Flask web app ที่เชื่อมต่อกับ Stable Diffusion WebUI (Forge) เพื่อ generate/edit ภาพด้วย AI

---

## สมาชิกทีม (Group 04)

| Role | หน้าที่ |
|------|---------|
| คนที่ 1 | Frontend / Jinja2 Templates |
| คนที่ 2 | Flask Backend / QA-DevOps |
| คนที่ 3 | Forge AI / Stable Diffusion WebUI |

---

## Prerequisites

- Python 3.11+
- Git
- (ตัวเลือก) Conda / Miniconda

---

## การติดตั้ง

### วิธีที่ 1: ใช้ Conda (แนะนำ)

```bash
# Clone โปรเจค
git clone https://github.com/boss2912/luma-webapp-g04.git
cd luma-webapp-g04/luma-webapp

# สร้าง environment จาก environment.yml
conda env create -f environment.yml

# Activate environment
conda activate luma

# รันโปรเจค
python run.py
```

หลังรันโปรเจคสำเร็จ (เปิดค้างไว้ใน terminal อีกหน้าต่าง) ตรวจสอบว่าติดตั้งถูกต้องด้วย:
```bash
pytest
```

### วิธีที่ 2: ใช้ pip + venv

#### Windows (PowerShell)
```powershell
git clone https://github.com/boss2912/luma-webapp-g04.git
cd luma-webapp-g04\luma-webapp

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

python run.py
```

ตรวจสอบว่าติดตั้งถูกต้อง (เปิด terminal อีกหน้าต่าง, activate .venv เหมือนเดิม):
```powershell
pytest
```

#### Mac / Linux (bash/zsh)
```bash
git clone https://github.com/boss2912/luma-webapp-g04.git
cd luma-webapp-g04/luma-webapp

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python run.py
```

ตรวจสอบว่าติดตั้งถูกต้อง (เปิด terminal อีกหน้าต่าง, activate .venv เหมือนเดิม):
```bash
pytest
```

---

## ตั้งค่า instance/config.py

> ⚠️ ไฟล์นี้ **ไม่ push ขึ้น git** เพราะเก็บค่าลับ — ต้องสร้างเองในแต่ละเครื่อง

คัดลอกไฟล์ตัวอย่างแล้วแก้ค่าตามต้องการ:

**Windows (PowerShell):**
```powershell
copy instance\config.py.example instance\config.py
```

**Mac / Linux:**
```bash
cp instance/config.py.example instance/config.py
```

จากนั้นเปิด `instance/config.py` แก้ค่าที่จำเป็น:

```python
# instance/config.py

SECRET_KEY = "ใส่ random key ที่นี่"  # เปลี่ยนก่อน deploy จริง

SQLALCHEMY_DATABASE_URI = "sqlite:///luma.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# IP/URL ของเครื่องที่รัน Stable Diffusion WebUI (Forge)
FORGE_AI_ENDPOINT = "http://localhost:7860/sdapi/v1/txt2img"
# เปลี่ยนเป็น IP เครื่องคนที่ 3 ถ้ารันบน network เดียวกัน เช่น:
# FORGE_AI_ENDPOINT = "http://192.168.1.50:7860/sdapi/v1/txt2img"
```
---

## โครงสร้างโปรเจค

luma-webapp/
├── run.py ← รัน: python run.py
├── requirements.txt ← pip dependencies
├── environment.yml ← conda environment
├── .gitignore
│
├── app/
│ ├── init.py ← create_app() factory
│ ├── models.py ← SQLAlchemy: User, Asset, Job
│ ├── routes/
│ │ ├── auth.py ← /auth/login, /auth/register, /auth/logout
│ │ ├── api.py ← /api/generate, /api/assets
│ │ └── main.py ← /, /dashboard
│ ├── templates/ ← Jinja2 HTML
│ ├── static/css/ ← style.css
│ └── utils/logger.py ← logging config
│
├── tests/
│ ├── conftest.py ← ตั้งค่า path ให้ pytest หา app/ เจอ
│ └── test_system_check.py
│
└── instance/
├── config.py ← SECRET_KEY, DB URI (ไม่ push!)
└── config.py.example ← ไฟล์ตัวอย่าง (push ได้ ไม่มีค่าลับจริง)

---

## API Endpoints

| Method | Endpoint | Auth | คำอธิบาย |
|--------|----------|------|----------|
| GET | `/` | ไม่ต้อง | หน้าแรก |
| GET | `/dashboard` | ต้อง login | Dashboard + Generate Form |
| POST | `/auth/register` | ไม่ต้อง | สมัครสมาชิก |
| POST | `/auth/login` | ไม่ต้อง | เข้าสู่ระบบ |
| GET | `/auth/logout` | ต้อง login | ออกจากระบบ |
| POST | `/api/generate` | ต้อง login | Generate ภาพ |
| GET | `/api/assets` | ต้อง login | ดูรูปทั้งหมด |

### ตัวอย่าง POST /api/generate

```json
// Request
POST /api/generate
Content-Type: application/json
{
  "prompt": "a cat wizard, digital art, 4k"
}

// Response (success)
{
  "status": "success",
  "asset_id": 1,
  "image_url": "/static/generated/asset_1_1720000000.png"
}

// Response (error — Forge AI ไม่ทำงาน)
{
  "error": "เชื่อมต่อ Forge AI ไม่ได้ — ตรวจสอบว่า Stable Diffusion WebUI กำลังทำงานอยู่"
}
```

---

## Database Models
users → id, username, email, password_hash, created_at
assets → id, user_id, filename, prompt, tags, created_at
jobs → id, user_id, status, result_asset_id, created_at

---

## การแก้ปัญหาเบื้องต้น

| ปัญหา | วิธีแก้ |
|-------|---------|
| `ModuleNotFoundError: flask` | `pip install -r requirements.txt` |
| `502 Forge AI ไม่ตอบสนอง` | ตรวจสอบว่า SD WebUI (Forge) กำลังทำงาน และ `FORGE_AI_ENDPOINT` ถูกต้อง |
| `python run.py` แล้วไม่มี instance/config.py | คัดลอกจาก `instance/config.py.example` ตามขั้นตอนด้านบน |
| `pytest` แล้ว `ModuleNotFoundError: No module named 'app'` | ตรวจสอบว่ามีไฟล์ `tests/conftest.py` อยู่ และรัน `pytest` จากโฟลเดอร์ `luma-webapp/` เท่านั้น (ไม่ใช่รันไฟล์ตรงๆ ด้วย path เต็ม) |
| Database error | ลบ `instance/luma.db` แล้วรันใหม่ |
