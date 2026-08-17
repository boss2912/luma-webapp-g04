# LUMA v1 — Code Snapshot (เก็บก่อนรีเซ็ตโครงสร้าง)

> ไฟล์นี้เก็บ **source code ทั้งหมดของ `luma-webapp/` เวอร์ชัน v1 แบบคำต่อคำ**
> ณ commit ที่รวม PR #10 / #11 / #12 เข้าด้วยกันแล้ว (pytest 33/33 ผ่าน)
>
> **จุดประสงค์**: หลังจากนี้โค้ด v1 จะถูกลบออกเพื่อวางโครงสร้างใหม่ตามสเปกของอาจารย์
> ไฟล์นี้คือบันทึกอ้างอิงว่าเคยเขียนอะไรไว้ เพื่อหยิบ logic กลับมาใช้ได้โดยไม่ต้องขุด git history
>
> โค้ดตัวจริงยังอยู่ใน git ด้วย — ดูได้จาก tag `backup/pre-restructure-develop`


## สารบัญไฟล์

- `luma-webapp/.gitignore`
- `luma-webapp/CONTRIBUTING.md`
- `luma-webapp/INSTALL.md`
- `luma-webapp/README.md`
- `luma-webapp/environment.yml`
- `luma-webapp/requirements.txt`
- `luma-webapp/run.py`
- `luma-webapp/app/__init__.py`
- `luma-webapp/app/models.py`
- `luma-webapp/app/routes/__init__.py`
- `luma-webapp/app/routes/api.py`
- `luma-webapp/app/routes/auth.py`
- `luma-webapp/app/routes/main.py`
- `luma-webapp/app/static/css/style.css`
- `luma-webapp/app/templates/base.html`
- `luma-webapp/app/templates/dashboard.html`
- `luma-webapp/app/templates/index.html`
- `luma-webapp/app/templates/auth/login.html`
- `luma-webapp/app/templates/auth/register.html`
- `luma-webapp/app/utils/__init__.py`
- `luma-webapp/app/utils/logger.py`
- `luma-webapp/instance/config.py.example`
- `luma-webapp/instance/luma.db` *(binary — ไม่ฝังเนื้อหา)*
- `luma-webapp/tests/__init__.py`
- `luma-webapp/tests/conftest.py`
- `luma-webapp/tests/test_assets.py`
- `luma-webapp/tests/test_assets_delete.py`
- `luma-webapp/tests/test_auth.py`
- `luma-webapp/tests/test_e2e_flow.py`
- `luma-webapp/tests/test_generate_params.py`
- `luma-webapp/tests/test_models.py`
- `luma-webapp/tests/test_system_check.py`


---


## `luma-webapp/.gitignore`

```
# =============================================================================
# LUMA Web App — .gitignore
# =============================================================================

# ── Python bytecode ──────────────────────────────────────────────────────────
__pycache__/
*.py[cod]
*$py.class
*.pyo

# ── Flask / SQLite database (ห้าม push ขึ้น git!) ──────────────────────────
instance/*.db
instance/*.sqlite
instance/*.sqlite3

# ── Secret config (ห้าม push ขึ้น git!) ────────────────────────────────────
# Fix F09: เดิม SECRET_KEY placeholder ถูก push ขึ้น git เพราะบรรทัดนี้ถูก comment ไว้
instance/config.py
.env
.env.*

# ── Virtual environment ───────────────────────────────────────────────────────
.venv/
venv/
env/
ENV/

# ── Conda environment (local envs) ───────────────────────────────────────────
# ไม่ต้อง push โฟลเดอร์ env ของ conda
envs/

# ── Flask-Migrate / Alembic (optional — ถ้าต้องการ track migrations ให้ลบบรรทัดนี้)
# migrations/

# ── IDE / Editor ──────────────────────────────────────────────────────────────
.vscode/
.idea/
*.swp
*.swo
*~

# ── OS ────────────────────────────────────────────────────────────────────────
.DS_Store
Thumbs.db
desktop.ini

# ── Generated image uploads (ถ้าเก็บ local) ──────────────────────────────────
# Fix F05: ย้ายที่เก็บรูปออกจาก app/static/generated/ (Flask เสิร์ฟให้ทุกคนเห็นฟรี)
# มาไว้ที่ app/generated/ แทน (เสิร์ฟผ่าน route ที่เช็ค ownership เท่านั้น)
app/static/uploads/
app/generated/

# ── Logs ──────────────────────────────────────────────────────────────────────
*.log
logs/

# ── Coverage / Testing ────────────────────────────────────────────────────────
.coverage
htmlcov/
.pytest_cache/
.tox/

# ── Build artifacts ───────────────────────────────────────────────────────────
dist/
build/
*.egg-info/
```


## `luma-webapp/CONTRIBUTING.md`

````markdown
# 🤝 Contributing Guide — LUMA Web App (Group 04)

> ภาษาไทย · English (bilingual guide for the team)

---

## 🌿 Git Branching Strategy

### โครงสร้าง Branch / Branch Structure

```
main     ────────────────────────────────● ← release เท่านั้น / release only
                                         ↑ PR only (หัวหน้า approve)
develop  ──●──●──●──●──●──●──●──●──●──●─● ← รวมงานทีม / integration branch
           ↑       ↑       ↑
           │   feature/forge-ai
           │               ↑
feature/backend-auth    feature/ui-frontend
```

### กฎเหล็ก / Non-Negotiable Rules

| 🇹🇭 ภาษาไทย | 🇬🇧 English |
|------------|-----------|
| ❌ ห้าม push ตรงเข้า `main` หรือ `develop` | ❌ Never push directly to `main` or `develop` |
| ✅ ต้องเปิด Pull Request ทุกครั้ง | ✅ Always open a Pull Request |
| ✅ ต้องมีคน review อย่างน้อย 1 คน | ✅ At least 1 reviewer required |
| ✅ sync `develop` กลับเข้า branch ตัวเองสัปดาห์ละครั้ง | ✅ Sync `develop` into your branch weekly |

---

## 👤 Branch ของแต่ละคน / Branch Assignment

| คน / Person | Branch | หน้าที่ / Responsibility |
|-------------|--------|------------------------|
| คุณ (หัวหน้า) / Team Lead | `feature/backend-auth` | Flask Backend, Auth, API, DB |
| คนที่ 2 / Member 2 | `feature/forge-ai` | Forge AI integration, Testing |
| คนที่ 3 / Member 3 | `feature/ui-frontend` | Templates, CSS, JavaScript |

---

## 📋 Workflow ประจำวัน / Daily Workflow

### 1. เริ่มวันทำงาน / Start of Day

```bash
# อัปเดต develop ล่าสุดก่อน / Always pull latest develop first
git checkout develop
git pull origin develop

# กลับไป branch ตัวเอง แล้ว sync develop / Go back to your branch and sync
git checkout feature/your-feature
git merge develop
# ถ้ามี conflict → แก้แล้วรัน: git add . && git commit -m "merge: sync develop"
```

### 2. ระหว่างทำงาน / During Work

```bash
# บันทึกงาน / Save your work
git add .
git commit -m "feat: อธิบายสั้นๆ / brief description"

# Push ขึ้น branch ตัวเอง / Push to your branch
git push origin feature/your-feature
```

### 3. ส่งงาน / Submit Work (PR)

```bash
# ตรวจสอบก่อน push / Check before pushing
git status                          # ต้องไม่มี instance/config.py, *.db
git log --oneline -5                # commit message อ่านรู้เรื่อง
python run.py                       # รันได้โดยไม่ error
```

จากนั้นไปที่ GitHub → Pull requests → New pull request:
- **base:** `develop`  ← **compare:** `feature/your-feature`
- เขียน description: ทำอะไร, ทดสอบอะไรแล้ว, screenshot (ถ้ามี)
- Assign reviewer: `boss2912` (หัวหน้า)

### 4. ส่งงานจริง / Release (หัวหน้าเท่านั้น / Lead only)

```bash
# เปิด PR: develop → main บน GitHub web เท่านั้น
# ห้าม git push ตรงเข้า main
```

---

## 📝 Commit Message Format

```
<type>: <short description in Thai or English>
```

| Type | ใช้เมื่อ / When to use |
|------|----------------------|
| `feat:` | เพิ่ม feature ใหม่ / New feature |
| `fix:` | แก้ bug / Bug fix |
| `docs:` | แก้ documentation / Documentation change |
| `style:` | แก้ CSS, format / Style/format change |
| `refactor:` | ปรับโครงสร้าง ไม่เพิ่ม feature / Refactor without new feature |
| `test:` | เพิ่ม/แก้ test / Test changes |
| `chore:` | งาน maintenance / Maintenance tasks |

**ตัวอย่าง / Examples:**
```bash
git commit -m "feat: เพิ่มระบบ login/register ครบวงจร"
git commit -m "fix: แก้ FORGE_AI_ENDPOINT อ่านจาก config แทน hardcode"
git commit -m "style: ปรับ CSS dashboard ให้ responsive"
git commit -m "docs: เพิ่ม API endpoint docs ใน README"
```

---

## ✅ Self-Review Checklist (ก่อน Push ทุกครั้ง)

```
[ ] git status ไม่มี instance/config.py, *.db, .venv/ ในรายการ
[ ] python run.py รันได้โดยไม่มี error
[ ] ถ้าแก้ models.py → ทดสอบ db.create_all() ใหม่
[ ] commit message อ่านแล้วเข้าใจว่าทำอะไร
[ ] ไม่ hardcode IP, password, API key ในโค้ด
```

---

## 🆘 แก้ปัญหาที่พบบ่อย / Common Issues

| ปัญหา / Problem | วิธีแก้ / Solution |
|----------------|-------------------|
| `ModuleNotFoundError: flask` | `pip install -r requirements.txt` |
| `502 Forge AI ไม่ตอบสนอง` | เช็ค `FORGE_AI_ENDPOINT` ใน config, เช็คว่า SD WebUI รันอยู่ |
| Merge conflict ใน templates | ติดต่อหัวหน้า (boss2912) ก่อนแก้ |
| `instance/luma.db` หายไป | ปกติ — สร้างใหม่เองโดยรัน `python run.py` |
| ลืม pull develop ก่อนทำงาน | `git checkout develop && git pull && git checkout feature/... && git merge develop` |
````


## `luma-webapp/INSTALL.md`

````markdown
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
````


## `luma-webapp/README.md`

```markdown
# LUMA WebApp - Image Processing Project Backend

โปรเจกต์นี้รองรับการติดตั้งทั้งผู้ที่ใช้ **Conda** และ **Python มาตรฐาน (venv)** กรุณาเลือกวิธีติดตั้งตามระบบที่คุณใช้ด้านล่างนี้:

---

## 🟢 วิธีที่ 1: สำหรับผู้ที่ใช้ Conda (แนะนำ)

### 1. สร้าง Environment จากไฟล์กำหนดค่า
conda env create -f environment.yml

### 2. เปิดใช้งาน Environment
conda activate luma

### 3. รันเซิร์ฟเวอร์
python run.py

---

## 🔵 วิธีที่ 2: สำหรับผู้ที่ใช้ Python มาตรฐาน (venv + pip)
*ข้อกำหนด: เครื่องของคุณต้องติดตั้ง Python 3.11 ไว้แล้ว*

### 1. สร้าง Virtual Environment จำลองในโฟลเดอร์โปรเจกต์
python -m venv venv

### 2. เปิดใช้งาน Environment (เลือกตามระบบปฏิบัติการของคุณ)
- **Windows (PowerShell):**
  venv\Scripts\Activate.ps1
- **Windows (CMD):**
  venv\Scripts\activate.bat
- **macOS / Linux:**
  source venv/bin/activate

*สังเกตหน้าบรรทัดคำสั่งต้องมีคำว่า `(venv)` ขึ้นมา*

### 3. อัปเกรดเครื่องมือและติดตั้งแพ็กเกจทั้งหมด
python -m pip install --upgrade pip
pip install -r requirements.txt

### 4. รันเซิร์ฟเวอร์
python run.py

---

## 🚀 การเข้าใช้งานระบบ
เมื่อรันเซิร์ฟเวอร์สำเร็จแล้ว ให้เปิดเว็บเบราว์เซอร์ไปที่:
http://127.0.0.1:5000
```


## `luma-webapp/environment.yml`

```yaml
name: luma
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.11
  - pip
  - pip:
      - Flask==3.0.3
      - Flask-Login==0.6.3
      - Flask-Migrate==4.0.7
      - Flask-SQLAlchemy==3.1.1
      - Flask-WTF==1.2.1
      - WTForms==3.1.2
      - requests==2.32.3
      - Pillow==10.4.0
```


## `luma-webapp/requirements.txt`

```text
# LUMA Web App — Direct Dependencies Only
# Generated: 2026-07-13
# Install: pip install -r requirements.txt

# ── Web Framework ─────────────────────────────────────────────────────────────
Flask==3.0.3

# ── Flask Extensions ──────────────────────────────────────────────────────────
Flask-Login==0.6.3
Flask-Migrate==4.0.7
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1

# ── Form Validation ───────────────────────────────────────────────────────────
WTForms==3.1.2

# ── HTTP Client (เรียก Forge AI endpoint) ────────────────────────────────────
requests==2.32.3

# ── Image Processing (บันทึก/แปลง base64 → ไฟล์ภาพ) ─────────────────────────
Pillow==10.4.0

# ── WSGI Server (ใช้ใน production แทน Flask dev server) ──────────────────────
# gunicorn==22.0.0   ← uncomment ถ้า deploy บน Linux/Mac

# ── Testing (Issue #6: E2E System Testing) ────────────────────────────────────
pytest==8.3.3
```


## `luma-webapp/run.py`

```python
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
```


## `luma-webapp/app/__init__.py`

```python
"""
Application Factory Pattern
----------------------------
Input   : Flask config (จาก instance/config.py)
Process : สร้าง Flask app -> ผูก SQLAlchemy -> ผูก Login Manager -> ลงทะเบียน Blueprint
Output  : app object พร้อมใช้งาน (import ไปใช้ใน run.py)
"""

from flask import Flask, jsonify, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

# --- Extensions (ประกาศไว้นอกฟังก์ชัน เพื่อให้ import ไปใช้ที่อื่นได้ เช่น models.py) ---
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
# Fix F06: เดิมติดตั้ง Flask-WTF ไว้ใน requirements.txt แต่ไม่เคยเปิดใช้ CSRFProtect เลย
# ทำให้ฟอร์ม login/register/logout โดน CSRF attack ได้ (เว็บอื่นสั่งให้ browser
# ยิง POST มาที่เว็บนี้แทนผู้ใช้ได้โดยไม่รู้ตัว)
csrf = CSRFProtect()


def create_app(config_overrides=None):
    app = Flask(__name__, instance_relative_config=True)

    # 1) โหลด config จาก instance/config.py (เก็บ SECRET_KEY, DB URI ที่นี่ ไม่ push ขึ้น git)
    # silent=True: ไฟล์นี้ไม่ถูก track ใน git แล้ว (F09) เครื่องที่เพิ่ง clone หรือ
    # test runner (Issue #6) จะยังไม่มีไฟล์นี้ — ให้ทำงานต่อได้ด้วยค่า default
    # แทนที่จะ crash ตั้งแต่ตอน import
    app.config.from_pyfile("config.py", silent=True)
    app.config.setdefault("SECRET_KEY", "dev-only-insecure-key-set-real-one-in-instance-config-py")
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///luma.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config.setdefault("FORGE_AI_ENDPOINT", "http://localhost:7860/sdapi/v1/txt2img")

    if config_overrides:
        app.config.update(config_overrides)

    # 2) ผูก extensions เข้ากับ app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"

    # Fix F10: เดิม Flask-Login redirect ไปหน้า login (HTML) เสมอเวลาไม่ได้ login
    # แม้จะเป็น /api/* ที่ frontend คาดหวัง JSON ก็ตาม ทำให้ fetch() ฝั่ง JS
    # พยายาม parse HTML เป็น JSON แล้ว error อธิบายไม่ได้ว่าเกิดอะไรขึ้น
    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/api/"):
            return jsonify({"error": "unauthorized — กรุณาเข้าสู่ระบบก่อน / please log in"}), 401
        return redirect(url_for("auth.login", next=request.path))

    # 3) ตั้งค่า Logging ผ่าน utils/logger.py (แยก concern ออกจาก factory)
    from app.utils.logger import setup_logging
    setup_logging(app)

    # 4) ลงทะเบียน Blueprint (แยกไฟล์ตามหน้าที่ auth / api / main)
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Fix F06 (ต่อ): ยกเว้น CSRF ให้ /api/* เพราะเป็น JSON endpoint ล้วน ไม่ได้ใช้ฟอร์ม
    # HTML — ป้องกัน CSRF ของ JSON API ด้วยการเช็ค Content-Type แทน (browser ฟอร์มธรรมดา
    # ยิง JSON ตรงๆ ไม่ได้อยู่แล้ว) ส่วนฟอร์ม HTML จริง (login/register/logout) ยังคง
    # บังคับ csrf_token ตามปกติ
    csrf.exempt(api_bp)

    # 5) import models เพื่อให้ SQLAlchemy รู้จักตาราง แล้วสร้างไฟล์ DB ถ้ายังไม่มี
    from app import models
    with app.app_context():
        db.create_all()

    return app
```


## `luma-webapp/app/models.py`

```python
"""
Database Models
----------------
Input   : ข้อมูล user สมัคร / รูปที่ generate / งานที่ยิงไป Forge AI
Process : กำหนดตาราง SQL ผ่าน SQLAlchemy ORM
Output  : ตาราง users, assets, jobs ใน SQLite/PostgreSQL
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assets = db.relationship("Asset", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"


class Asset(db.Model):
    """เก็บรูปที่ user generate/edit ไว้ใน Asset Hub (ตามสไลด์ Smart Canvas / Asset Hub)"""
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    prompt = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(255), nullable=True)  # เช่น "portrait,anime,4k"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Asset id={self.id} user_id={self.user_id} filename={self.filename!r}>"


class Job(db.Model):
    """เก็บสถานะงานที่ยิงไป Forge AI (queue / pending / done / failed)"""
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    prompt = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="pending")  # pending, running, done, failed
    result_asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    result_asset = db.relationship("Asset", foreign_keys=[result_asset_id])

    def __repr__(self):
        return f"<Job id={self.id} user_id={self.user_id} status={self.status!r}>"


@login_manager.user_loader
def load_user(user_id):
    # User.query.get() ถูก deprecated ใน SQLAlchemy 2.x → ใช้ db.session.get() แทน
    return db.session.get(User, int(user_id))
```


## `luma-webapp/app/routes/__init__.py`

```python

```


## `luma-webapp/app/routes/api.py`

```python
"""
API Blueprint
-------------
Input   : JSON prompt จาก frontend (เช่น {"prompt": "a cat wizard"})
Process : ยิง request ต่อไปที่ Forge AI service (คนที่ 3 เป็นคนเปิด endpoint นี้ไว้)
Output  : JSON ที่มี path/URL ของภาพที่ generate เสร็จ แล้วบันทึกลง DB (Asset)
"""

import os
import base64
import uuid
import requests
from flask import Blueprint, request, jsonify, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from app import db
from app.models import Asset
from app.utils.logger import get_logger

logger = get_logger(__name__)
api_bp = Blueprint("api", __name__)

# Issue #5: ขอบเขตพารามิเตอร์ที่ยอมรับ — เช็คก่อนยิงต่อไปที่ Forge AI เสมอ
ALLOWED_DIMENSIONS = (512, 768, 1024)
MIN_STEPS, MAX_STEPS = 1, 50
DEFAULT_STEPS = 20
MIN_CFG_SCALE, MAX_CFG_SCALE = 1, 30
DEFAULT_CFG_SCALE = 7

# Fix F05 (IDOR): เดิมเก็บใน app/static/generated/ ซึ่ง Flask เสิร์ฟให้ใครก็ได้
# เห็นผ่าน URL ตรงๆ โดยไม่เช็ค login เลย (แค่รู้/เดา URL ก็ดูรูปคนอื่นได้)
# ย้ายออกมานอก static/ แล้วบังคับให้ดูผ่าน route get_asset_image() ที่เช็ค
# ownership เท่านั้น — ใช้ absolute path ยึดกับตำแหน่งไฟล์นี้เอง (ไม่ใช่ relative
# path ที่พึ่ง current working directory ตอนรัน ซึ่งเคยทำให้ route หาไฟล์ไม่เจอ)
UPLOAD_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "generated")
)


def _get_forge_endpoint() -> str:
    """อ่าน FORGE_AI_ENDPOINT จาก config (ป้องกัน hardcode URL)"""
    return current_app.config.get(
        "FORGE_AI_ENDPOINT", "http://localhost:7860/sdapi/v1/txt2img"
    )


def _save_base64_image(b64_string: str, filename: str) -> str:
    """
    แปลง base64 string → บันทึกเป็นไฟล์ภาพ
    Return: relative path สำหรับ serve ผ่าน Flask static
    """
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(b64_string))
    # คืนแค่ชื่อไฟล์ (ไม่ผูกกับ static/ อีกต่อไป — ดูรูปต้องผ่าน
    # get_asset_image() ที่เช็ค ownership เท่านั้น)
    return filename


def _validate_generate_params(data):
    """
    Issue #5: ตรวจ negative_prompt / steps / cfg_scale / width / height ก่อนส่งต่อ
    Forge AI เสมอ — ไม่มี field ไหนที่จำเป็นต้องส่งมา (ทุกตัวมีค่า default)
    Return: (params dict, error message หรือ None)
    """
    params = {
        "negative_prompt": "",
        "steps": DEFAULT_STEPS,
        "cfg_scale": DEFAULT_CFG_SCALE,
        "width": 512,
        "height": 512,
    }

    negative_prompt = data.get("negative_prompt", "")
    if negative_prompt is not None:
        if not isinstance(negative_prompt, str):
            return None, "negative_prompt ต้องเป็น string / negative_prompt must be a string"
        params["negative_prompt"] = negative_prompt.strip()

    if "steps" in data and data["steps"] is not None:
        steps = data["steps"]
        if not isinstance(steps, int) or isinstance(steps, bool) or not (MIN_STEPS <= steps <= MAX_STEPS):
            return None, f"steps ต้องเป็นจำนวนเต็มระหว่าง {MIN_STEPS}-{MAX_STEPS} / steps must be an integer between {MIN_STEPS} and {MAX_STEPS}"
        params["steps"] = steps

    if "cfg_scale" in data and data["cfg_scale"] is not None:
        cfg_scale = data["cfg_scale"]
        if not isinstance(cfg_scale, (int, float)) or isinstance(cfg_scale, bool) or not (MIN_CFG_SCALE <= cfg_scale <= MAX_CFG_SCALE):
            return None, f"cfg_scale ต้องเป็นตัวเลขระหว่าง {MIN_CFG_SCALE}-{MAX_CFG_SCALE} / cfg_scale must be a number between {MIN_CFG_SCALE} and {MAX_CFG_SCALE}"
        params["cfg_scale"] = cfg_scale

    for dim in ("width", "height"):
        if dim in data and data[dim] is not None:
            value = data[dim]
            if value not in ALLOWED_DIMENSIONS:
                allowed = "/".join(str(d) for d in ALLOWED_DIMENSIONS)
                return None, f"{dim} ต้องเป็นหนึ่งใน {allowed} / {dim} must be one of {allowed}"
            params[dim] = value

    return params, None


@api_bp.route("/generate", methods=["POST"])
@login_required
def generate_image():
    # silent=True: ถ้า body ไม่ใช่ JSON ที่ parse ได้ จะได้ None แทนที่จะโยน
    # exception ขึ้นมาเป็น 500 — เช็คแล้วตอบ 400 ที่อ่านง่ายกว่าแทน
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "ต้องส่ง JSON body / request body must be JSON"}), 400

    prompt = data.get("prompt", "")
    # Fix F04: เดิมถ้า prompt ไม่ใช่ string (เช่น {"prompt": 12345}) การเรียก
    # .strip() จะ crash เป็น 500 — เช็ค type ก่อนเสมอ
    if not isinstance(prompt, str):
        return jsonify({"error": "prompt ต้องเป็น string / prompt must be a string"}), 400
    prompt = prompt.strip()

    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    gen_params, error = _validate_generate_params(data)
    if error:
        return jsonify({"error": error}), 400

    forge_url = _get_forge_endpoint()
    logger.info(f"[generate] user={current_user.id} prompt='{prompt[:50]}' → {forge_url}")

    try:
        response = requests.post(
            forge_url,
            json={
                "prompt": prompt,
                **gen_params,
            },
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()

        # บันทึกรูปภาพจาก base64 (Forge AI ส่งกลับมาเป็น list)
        images = result.get("images", [])
        if not images:
            return jsonify({"error": "Forge AI ไม่ส่งรูปกลับมา"}), 502

        # Fix F11: เดิมใช้ int(time.time()) ความละเอียดแค่ระดับวินาที ถ้ามีคน
        # generate 2 ครั้งในวินาทีเดียวกัน ไฟล์ชื่อชนกันและไฟล์เก่าถูกทับ
        # เปลี่ยนเป็น uuid4 ที่ไม่ซ้ำกันแทบจะแน่นอน
        filename = f"asset_{current_user.id}_{uuid.uuid4().hex[:12]}.png"
        saved_filename = _save_base64_image(images[0], filename)
        logger.info(f"[generate] saved image → {saved_filename}")

        asset = Asset(
            user_id=current_user.id,
            filename=saved_filename,
            prompt=prompt,
        )
        db.session.add(asset)
        db.session.commit()

        return jsonify({
            "status": "success",
            "asset_id": asset.id,
            "image_url": f"/api/assets/{asset.id}/image",
        })

    except requests.exceptions.ConnectionError:
        logger.error(f"[generate] Forge AI ไม่ตอบสนอง: {forge_url}")
        return jsonify({"error": f"เชื่อมต่อ Forge AI ไม่ได้ ({forge_url}) — ตรวจสอบว่า Stable Diffusion WebUI กำลังทำงานอยู่"}), 502
    except requests.exceptions.Timeout:
        logger.error("[generate] Forge AI timeout")
        return jsonify({"error": "Forge AI ใช้เวลานานเกินไป (timeout 120s)"}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"[generate] error: {e}")
        return jsonify({"error": f"Forge AI error: {str(e)}"}), 502


@api_bp.route("/assets", methods=["GET"])
@login_required
def list_assets():
    """ดึงรายการ Asset ทั้งหมดของ user ที่ login อยู่"""
    assets = Asset.query.filter_by(user_id=current_user.id).order_by(Asset.created_at.desc()).all()
    return jsonify([
        {
            "id": a.id,
            "filename": a.filename,
            "prompt": a.prompt,
            "tags": a.tags,
            "created_at": a.created_at.isoformat(),
            "image_url": f"/api/assets/{a.id}/image",
        }
        for a in assets
    ])


def _get_owned_asset_or_404(asset_id):
    """
    ดึง Asset ที่ current_user เป็นเจ้าของเท่านั้น — ใช้ร่วมกันทั้ง get_asset_image()
    และ delete_asset() กันโค้ดซ้ำ
    ตอบ 404 (ไม่ใช่ 403) ทั้งกรณี "ไม่มี asset นี้" และ "มีแต่ไม่ใช่ของเรา"
    เพื่อไม่บอกผู้โจมตีว่า asset_id นั้นมีอยู่จริงหรือเปล่า — ลดข้อมูลที่รั่วไหลออกไป
    """
    # db.session.get() แทน Asset.query.get() ที่ deprecated ใน SQLAlchemy 2.x
    # (ดู models.py: load_user() เตือนเรื่องเดียวกันนี้ไว้แล้วสำหรับ User)
    asset = db.session.get(Asset, asset_id)
    if asset is None or asset.user_id != current_user.id:
        abort(404)
    return asset


@api_bp.route("/assets/<int:asset_id>/image", methods=["GET"])
@login_required
def get_asset_image(asset_id):
    """
    Fix F05 (IDOR): เดิมรูปถูกเก็บใน app/static/generated/ ทำให้ Flask เสิร์ฟ
    ให้ทุกคนที่รู้/เดา URL เห็นได้เลย ไม่ต้อง login ไม่ต้องเป็นเจ้าของ
    ตอนนี้ต้อง (1) login และ (2) เป็นเจ้าของ asset นั้นเท่านั้นถึงจะดูรูปได้
    """
    asset = _get_owned_asset_or_404(asset_id)
    return send_from_directory(UPLOAD_FOLDER, os.path.basename(asset.filename))


@api_bp.route("/assets/<int:asset_id>", methods=["DELETE"])
@login_required
def delete_asset(asset_id):
    """
    Issue #3: ลบ asset ของตัวเอง — ลบทั้งไฟล์ภาพบนดิสก์และแถวใน DB
    หมายเหตุ CSRF: route นี้อยู่ใต้ api_bp ที่ยกเว้น CSRF ทั้ง blueprint (ดู
    app/__init__.py) แต่ DELETE ไม่ใช่ "simple method" ตาม Fetch spec เลยต้อง
    ผ่าน CORS preflight (OPTIONS) ก่อนเสมอ — เว็บนี้ไม่ได้ตั้งค่า CORS ให้ origin
    อื่นเลย เบราว์เซอร์จึงบล็อก cross-site DELETE ไว้ตั้งแต่ขั้น preflight แล้ว
    โดยไม่ต้องพึ่ง csrf_token
    """
    asset = _get_owned_asset_or_404(asset_id)

    filepath = os.path.join(UPLOAD_FOLDER, os.path.basename(asset.filename))
    try:
        os.remove(filepath)
    except FileNotFoundError:
        # ไฟล์หายไปจากดิสก์แล้วแต่แถว DB ยังอยู่ — ไม่ต้อง fail การลบ แค่ log ไว้
        logger.warning(f"[delete_asset] file already missing on disk: {filepath}")

    db.session.delete(asset)
    db.session.commit()
    logger.info(f"[delete_asset] user={current_user.id} deleted asset_id={asset_id}")

    return jsonify({"status": "deleted", "asset_id": asset_id})
```


## `luma-webapp/app/routes/auth.py`

```python
"""
Auth Blueprint
--------------
Input   : ฟอร์ม username/email/password จากผู้ใช้
Process : ตรวจสอบ / hash password / สร้าง session ผ่าน Flask-Login
Output  : redirect ไปหน้า main, หรือแสดง error รายฟิลด์ใต้ input ถ้าไม่ผ่าน
"""

from collections import defaultdict
from datetime import datetime
from time import time
from urllib.parse import urlparse

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

auth_bp = Blueprint("auth", __name__)

# Fix F14: in-memory rate limiter สำหรับ login (ไม่เพิ่ม dependency ใหม่)
# หมายเหตุ: เก็บใน memory ของ process เดียว ถ้า deploy หลาย worker/process
# แต่ละตัวจะนับแยกกัน — พอสำหรับ dev/งานกลุ่มนี้ ถ้า scale ขึ้นควรย้ายไป Redis
_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_ATTEMPTS = 5
_login_attempts = defaultdict(list)


def _is_rate_limited(key: str) -> bool:
    now = time()
    attempts = _login_attempts[key]
    attempts[:] = [t for t in attempts if now - t < _RATE_LIMIT_WINDOW_SECONDS]
    return len(attempts) >= _RATE_LIMIT_MAX_ATTEMPTS


def _record_failed_attempt(key: str) -> None:
    _login_attempts[key].append(time())


def _is_safe_next_url(target: str | None) -> bool:
    """
    Fix F01: เช็คว่า ?next= เป็น relative path ภายในเว็บนี้เท่านั้น ก่อนอนุญาตให้ redirect
    ปลอดภัย  : "/dashboard", "/api/assets"
    อันตราย  : "https://evil.example", "//evil.example" (protocol-relative)
    """
    if not target:
        return False
    parsed = urlparse(target)
    return not parsed.scheme and not parsed.netloc


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # ถ้า login แล้ว ให้ redirect ไป dashboard เลย
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    errors = {}
    username = email = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username:
            errors["username"] = "กรุณากรอกชื่อผู้ใช้ / Username is required"
        if not email:
            errors["email"] = "กรุณากรอกอีเมล / Email is required"
        # Fix F08: password policy ฝั่ง server (เดิมไม่เช็คความยาวเลย)
        if not password or len(password) < 8:
            errors["password"] = "รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร / Password must be at least 8 characters"

        if not errors:
            # Fix F07 + F12: เช็คซ้ำแบบไม่สนตัวพิมพ์ใหญ่-เล็ก และรวมข้อความ
            # username ซ้ำ / email ซ้ำ เป็นข้อความเดียวกัน กัน account enumeration
            # (ถ้าแยกข้อความ ผู้โจมตีจะรู้ได้ว่า username หรือ email ไหนมีอยู่จริงในระบบ)
            username_taken = User.query.filter(db.func.lower(User.username) == username.lower()).first()
            email_taken = User.query.filter(db.func.lower(User.email) == email).first()
            if username_taken or email_taken:
                errors["general"] = "ไม่สามารถสมัครด้วยข้อมูลนี้ได้ / Unable to register with this information"

        if not errors:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            logger.info(f"[register] new user: {username} ({email})")
            flash("สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ / Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", errors=errors, username=username, email=email)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # ถ้า login แล้ว ให้ redirect ไป dashboard เลย
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    errors = {}

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # key ด้วย email ที่พยายาม login ไม่ใช่ IP — ถ้า key ด้วย IP คนที่ใช้
        # network เดียวกัน (เช่น network มหาลัย/office) จะโดนบล็อกไปด้วยทั้งที่
        # ไม่เกี่ยวกับ account ที่ถูกโจมตี การ key ด้วย email จำกัดผลกระทบไว้แค่
        # account เป้าหมายเท่านั้น
        rate_limit_key = email or (request.remote_addr or "unknown")

        if _is_rate_limited(rate_limit_key):
            errors["general"] = (
                "พยายามเข้าสู่ระบบผิดหลายครั้งเกินไป กรุณารอสักครู่แล้วลองใหม่ / "
                "Too many failed attempts, please wait a moment"
            )
            return render_template("auth/login.html", errors=errors), 429

        user = User.query.filter(db.func.lower(User.email) == email).first()

        if user and user.check_password(password):
            login_user(user)
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"[login] user={user.username} logged in")
            # Fix F01: ยอม redirect เฉพาะ next ที่เป็น path ภายในเว็บนี้เท่านั้น
            next_page = request.args.get("next")
            if not _is_safe_next_url(next_page):
                next_page = None
            return redirect(next_page or url_for("main.dashboard"))

        _record_failed_attempt(rate_limit_key)
        logger.warning(f"[login] failed attempt for email={email}")
        errors["general"] = "อีเมลหรือรหัสผ่านไม่ถูกต้อง / Invalid email or password"

    return render_template("auth/login.html", errors=errors)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    # Fix F15: เปลี่ยนจาก GET เป็น POST-only (GET request ไม่ควรมี side effect
    # เช่นโดน prefetch/crawler ยิงแล้ว logout ผู้ใช้โดยไม่ตั้งใจ)
    logout_user()
    return redirect(url_for("main.index"))
```


## `luma-webapp/app/routes/main.py`

```python
"""
Main Blueprint
--------------
Input   : ผู้ใช้เข้าเว็บ /
Process : render หน้า index หรือ dashboard (ถ้า login แล้ว)
Output  : หน้า HTML (Jinja template)
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)
```


## `luma-webapp/app/static/css/style.css`

```css
/* app/static/css/style.css
   LUMA Web App — Base Styles (Dark Theme)
*/

/* ── Reset ────────────────────────────────────────────────────────────── */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Fix CSS bug (พบตอนวางแผน Issue #8): [hidden] ต้องซ่อน element เสมอ ไม่ว่า
   selector อื่นจะตั้ง display ไว้เป็นอะไรก็ตาม (เช่น .spinner { display: inline-block })
   ถ้าไม่มีกฎนี้ ลำดับ CSS ในไฟล์จะเป็นตัวตัดสินแทน ซึ่งพังง่ายเวลาแก้โค้ดทีหลัง */
[hidden] {
  display: none !important;
}

/* ── Variables ────────────────────────────────────────────────────────── */
:root {
  --color-primary: #6c63ff;
  --color-primary-dark: #4f47cc;
  --color-bg: #0f1115;
  --color-surface: #1a1d24;
  --color-surface-2: #22262f;
  --color-text: #e6e6e6;
  --color-text-muted: #9ca3af;
  --color-border: #2d3139;
  --color-danger: #ef4444;
  --color-success: #22c55e;
  --color-warning-bg: #2a2d34;
  --radius: 8px;
  --shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
  --nav-height: 60px;
}

/* ── Base ─────────────────────────────────────────────────────────────── */
body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background-color: var(--color-bg);
  color: var(--color-text);
  line-height: 1.6;
  min-height: 100vh;
}

a {
  color: var(--color-primary);
  text-decoration: none;
}
a:hover { text-decoration: underline; }

/* ── Navigation ───────────────────────────────────────────────────────── */
nav {
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow);
  min-height: var(--nav-height);
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  gap: 1rem;
  position: sticky;
  top: 0;
  z-index: 100;
  flex-wrap: wrap;
}

nav a {
  color: var(--color-text);
  font-weight: 500;
  padding: 0.4rem 0.8rem;
  border-radius: var(--radius);
  transition: background-color 0.15s;
}
nav a:hover {
  background-color: var(--color-surface-2);
  text-decoration: none;
}

/* Fix Issue #7: highlight ลิงก์ที่ active อยู่ */
nav a.active {
  background-color: var(--color-surface-2);
  color: var(--color-primary);
}

/* Brand/Logo */
nav a:first-child {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-right: auto;
  letter-spacing: 0.02em;
}
nav a.active:first-child { color: var(--color-primary); }

/* ปุ่ม Logout เป็น <form><button> แต่อยากให้หน้าตาเหมือนลิงก์ปกติในนาว (F15)
   หมายเหตุ: ต้อง qualify selector ด้วย .nav-logout-form (ไม่ใช้ .nav-link-btn เดี่ยวๆ)
   เพราะ .nav-link-btn อย่างเดียว specificity (0,1,0) แพ้ button[type="submit"]
   ด้านบน (0,1,1) ทำให้ปุ่ม Logout เคยได้พื้นหลังสีม่วงเต็มเหมือนปุ่ม submit ทั่วไป
   แทนที่จะเป็นลิงก์เปล่าตามที่ตั้งใจ */
.nav-logout-form { margin: 0; max-width: none; }
.nav-logout-form .nav-link-btn {
  background: none;
  border: none;
  color: var(--color-text);
  font-weight: 500;
  font-size: 1rem;
  font-family: inherit;
  padding: 0.4rem 0.8rem;
  border-radius: var(--radius);
  cursor: pointer;
  transition: background-color 0.15s;
}
.nav-logout-form .nav-link-btn:hover { background-color: var(--color-surface-2); }

/* Hamburger — ใช้เทคนิค checkbox hack ไม่ต้องพึ่ง JS (Issue #7: responsive mobile) */
.nav-toggle-checkbox { display: none; }
.nav-toggle-btn {
  display: none;
  font-size: 1.4rem;
  cursor: pointer;
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius);
}
.nav-toggle-btn:hover { background-color: var(--color-surface-2); }
.nav-links { display: flex; align-items: center; gap: 0.5rem; }

@media (max-width: 600px) {
  .nav-toggle-btn { display: block; }
  .nav-links {
    display: none;
    flex-direction: column;
    align-items: stretch;
    width: 100%;
    order: 3;
    padding-bottom: 0.75rem;
  }
  .nav-toggle-checkbox:checked ~ .nav-links { display: flex; }
  .nav-logout-form { width: 100%; }
  .nav-link-btn { width: 100%; text-align: left; }
}

/* ── Main Content ─────────────────────────────────────────────────────── */
main {
  max-width: 960px;
  margin: 2rem auto;
  padding: 0 1.25rem;
}

h1 { font-size: 1.8rem; margin-bottom: 1rem; font-weight: 700; }
h2 { font-size: 1.4rem; margin-bottom: 0.75rem; font-weight: 600; }
h3 { font-size: 1.1rem; margin-bottom: 0.5rem; font-weight: 600; }
p  { margin-bottom: 1rem; color: var(--color-text-muted); }

/* ── Flash Messages ───────────────────────────────────────────────────── */
.flashes {
  list-style: none;
  margin: 0.75rem 1.5rem;
}
.flashes li {
  border-radius: var(--radius);
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}
/* Fix Issue #7: เดิม flash message ทุกประเภทใช้สีเหลืองเดียวกันหมด แยกตาม
   category (success/error/warning ฯลฯ) ที่ backend ส่งมาให้แล้วจาก flash(msg, category) */
.flash-success {
  background-color: #16321f;
  border: 1px solid #22c55e;
  color: #4ade80;
}
.flash-error {
  background-color: #321616;
  border: 1px solid var(--color-danger);
  color: #f87171;
}
.flash-warning,
.flashes li:not(.flash-success):not(.flash-error) {
  background-color: #2d2a1a;
  border: 1px solid #6b5d00;
  color: #fbbf24;
}

/* ── Forms ────────────────────────────────────────────────────────────── */
form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 400px;
}

label {
  font-weight: 500;
  font-size: 0.88rem;
  color: var(--color-text-muted);
  margin-bottom: 0.1rem;
}

input[type="text"],
input[type="email"],
input[type="password"] {
  width: 100%;
  padding: 0.6rem 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  font-size: 1rem;
  background-color: var(--color-surface-2);
  color: var(--color-text);
  transition: border-color 0.15s, box-shadow 0.15s;
}

input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.2);
}

button,
button[type="submit"] {
  display: inline-block;
  padding: 0.6rem 1.4rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s, transform 0.1s;
  max-width: fit-content;
}

button:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
}
button:active { transform: translateY(0); }

/* ปุ่มตอนกด disabled (ระหว่าง generate) */
button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

/* ── Loading Spinner (Issue #8) ──────────────────────────────────────── */
.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  margin-left: 0.5rem;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  vertical-align: middle;
  animation: spin 0.7s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.text-muted {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

/* ── Card ─────────────────────────────────────────────────────────────── */
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 1.5rem;
  box-shadow: var(--shadow);
  margin-bottom: 1rem;
}

/* ── Auth Card (login/register) — Issue #9 ──────────────────────────────
   Fix: template อ้างถึง class นี้อยู่แล้ว (<section class="auth-card">)
   แต่ก่อนหน้านี้ไม่เคยมี CSS จริงมาก่อน เลยแสดงผลเหมือนไม่มี card เลย */
.auth-card {
  max-width: 400px;
  margin: 3rem auto;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 2rem 1.75rem;
  box-shadow: var(--shadow);
}
.auth-card h1 { font-size: 1.5rem; margin-bottom: 0.25rem; }
.auth-subtitle {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}
.auth-link {
  margin-top: 1.25rem;
  margin-bottom: 0;
  font-size: 0.88rem;
  text-align: center;
}

/* ── Field Errors (Issue #9: error ใต้ field ที่ผิดจริง) ─────────────── */
.field-error {
  color: var(--color-danger);
  font-size: 0.82rem;
  margin-top: 0.25rem;
  margin-bottom: 0;
}
.field-error-general {
  background-color: #321616;
  border: 1px solid var(--color-danger);
  border-radius: var(--radius);
  padding: 0.6rem 0.9rem;
  margin-bottom: 1rem;
}
input.input-error {
  border-color: var(--color-danger);
}
input.input-error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

/* ── Asset Grid (แสดง generated images) ─────────────────────────────── */
.asset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.asset-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--color-surface);
  transition: transform 0.15s, box-shadow 0.15s;
}
.asset-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.5);
}

.asset-card img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  display: block;
}

.asset-card .asset-info {
  padding: 0.5rem 0.75rem;
  font-size: 0.82rem;
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── Generate Result ──────────────────────────────────────────────────── */
#result {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: var(--color-surface-2);
  border-radius: var(--radius);
  font-family: monospace;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  min-height: 2.5rem;
}

/* ── Responsive ───────────────────────────────────────────────────────── */
@media (max-width: 600px) {
  main { padding: 0 0.75rem; margin: 1rem auto; }
  nav  { padding: 0 1rem; }
}
```


## `luma-webapp/app/templates/base.html`

```html
<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="LUMA — เว็บแอปสร้างภาพด้วย AI ผ่าน Stable Diffusion / AI image generation web app powered by Stable Diffusion">
  <title>LUMA - Learning-based Universal Media Artist</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
  <nav>
    <a href="{{ url_for('main.index') }}" class="{{ 'active' if request.endpoint == 'main.index' }}">LUMA</a>

    <!-- ปุ่ม hamburger โผล่เฉพาะจอมือถือ (ควบคุมด้วย CSS ล้วน ไม่ต้องใช้ JS) -->
    <input type="checkbox" id="nav-toggle" class="nav-toggle-checkbox">
    <label for="nav-toggle" class="nav-toggle-btn" aria-label="เปิด/ปิดเมนู">☰</label>

    <div class="nav-links">
      {% if current_user.is_authenticated %}
        <a href="{{ url_for('main.dashboard') }}" class="{{ 'active' if request.endpoint == 'main.dashboard' }}">Dashboard</a>
        <!-- Fix F15: logout ต้องเป็น POST ไม่ใช่ GET (GET ไม่ควรมี side effect) -->
        <form method="POST" action="{{ url_for('auth.logout') }}" class="nav-logout-form">
          <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
          <button type="submit" class="nav-link-btn">Logout</button>
        </form>
      {% else %}
        <a href="{{ url_for('auth.login') }}" class="{{ 'active' if request.endpoint == 'auth.login' }}">Login</a>
        <a href="{{ url_for('auth.register') }}" class="{{ 'active' if request.endpoint == 'auth.register' }}">Register</a>
      {% endif %}
    </div>
  </nav>

  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      <ul class="flashes">
        {% for category, message in messages %}
          <li class="flash-{{ category }}">{{ message }}</li>
        {% endfor %}
      </ul>
    {% endif %}
  {% endwith %}

  <main>
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```


## `luma-webapp/app/templates/dashboard.html`

```html
{% extends "base.html" %}
{% block content %}
  <h1>Dashboard ของ {{ user.username }} · {{ user.username }}'s Dashboard</h1>

  <form id="generate-form">
    <div class="form-group">
      <label for="prompt">Prompt</label>
      <input
        type="text"
        id="prompt"
        name="prompt"
        placeholder="เช่น a cat wizard, digital art"
        required
        autocomplete="off"
      >
    </div>
    <button type="submit" id="generate-btn">
      <span id="generate-btn-text">สร้างภาพ / Generate</span>
      <span id="generate-spinner" class="spinner" hidden aria-hidden="true"></span>
    </button>
  </form>

  <p id="generate-error" class="field-error field-error-general" hidden></p>

  <h2>แกลเลอรีของฉัน · My Gallery</h2>
  <div id="gallery" class="asset-grid"></div>
  <p id="gallery-empty" class="text-muted" hidden>ยังไม่มีรูปที่ generate ไว้ · No images generated yet</p>

  <script>
    const galleryEl = document.getElementById('gallery');
    const emptyEl = document.getElementById('gallery-empty');
    const form = document.getElementById('generate-form');
    const promptInput = document.getElementById('prompt');
    const btn = document.getElementById('generate-btn');
    const btnText = document.getElementById('generate-btn-text');
    const spinner = document.getElementById('generate-spinner');
    const errorBox = document.getElementById('generate-error');

    // กัน XSS: escape ข้อความ prompt ก่อนใส่ลง HTML (prompt มาจาก user input)
    function escapeHtml(str) {
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    }

    function assetCardHTML(asset) {
      const safePrompt = escapeHtml(asset.prompt || '');
      return (
        '<div class="asset-card">' +
          '<img src="' + asset.image_url + '" alt="' + safePrompt + '" loading="lazy">' +
          '<div class="asset-info" title="' + safePrompt + '">' + safePrompt + '</div>' +
        '</div>'
      );
    }

    function prependAsset(asset) {
      emptyEl.hidden = true;
      galleryEl.insertAdjacentHTML('afterbegin', assetCardHTML(asset));
    }

    // Fix: ตอนโหลดหน้า ต้องดึงรูปเก่าที่เคย generate ไว้แล้วมาโชว์ด้วย (ของเดิมไม่มีส่วนนี้เลย)
    async function loadGallery() {
      try {
        const res = await fetch('/api/assets');
        if (!res.ok) return;
        const assets = await res.json();
        if (assets.length === 0) {
          emptyEl.hidden = false;
          return;
        }
        emptyEl.hidden = true;
        galleryEl.insertAdjacentHTML('beforeend', assets.map(assetCardHTML).join(''));
      } catch (err) {
        console.error('โหลด gallery ไม่สำเร็จ / failed to load gallery', err);
      }
    }

    function setLoading(isLoading) {
      btn.disabled = isLoading;
      spinner.hidden = !isLoading;
      btnText.textContent = isLoading
        ? 'กำลังสร้าง... / Generating...'
        : 'สร้างภาพ / Generate';
    }

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const prompt = promptInput.value.trim();
      if (!prompt) return;

      errorBox.hidden = true;
      setLoading(true);

      try {
        const res = await fetch('/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt })
        });
        const data = await res.json();

        if (!res.ok) {
          errorBox.textContent = data.error || 'เกิดข้อผิดพลาด / Something went wrong';
          errorBox.hidden = false;
          return;
        }

        // Fix Issue #8: แสดงรูปทันทีหลัง API ตอบกลับ ไม่ต้อง reload หน้า
        prependAsset({ image_url: data.image_url, prompt: prompt });
        promptInput.value = '';
      } catch (err) {
        errorBox.textContent = 'เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ / Could not reach the server';
        errorBox.hidden = false;
      } finally {
        setLoading(false);
      }
    });

    loadGallery();
  </script>
{% endblock %}
```


## `luma-webapp/app/templates/index.html`

```html
{% extends "base.html" %}
{% block content %}
  <h1>ยินดีต้อนรับสู่ LUMA</h1>
  <p>Learning-based Universal Media Artist — สร้างและแก้ไขภาพด้วย AI</p>
{% endblock %}
```


## `luma-webapp/app/templates/auth/login.html`

```html
{% extends "base.html" %}
{% block content %}
<section class="auth-card">
  <h1>เข้าสู่ระบบ / Login</h1>
  <p class="auth-subtitle">ยินดีต้อนรับกลับ · Welcome back</p>

  {% if errors.general %}
    <p class="field-error field-error-general">{{ errors.general }}</p>
  {% endif %}

  <form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

    <div class="form-group">
      <label for="email">อีเมล / Email</label>
      <input
        type="email"
        id="email"
        name="email"
        placeholder="you@example.com"
        required
        autocomplete="email"
        class="{{ 'input-error' if errors.email }}"
      >
      {% if errors.email %}<p class="field-error">{{ errors.email }}</p>{% endif %}
    </div>

    <div class="form-group">
      <label for="password">รหัสผ่าน / Password</label>
      <input
        type="password"
        id="password"
        name="password"
        placeholder="••••••••"
        required
        autocomplete="current-password"
        class="{{ 'input-error' if errors.password }}"
      >
      {% if errors.password %}<p class="field-error">{{ errors.password }}</p>{% endif %}
    </div>

    <button type="submit" id="login-btn">เข้าสู่ระบบ / Sign In</button>
  </form>

  <p class="auth-link">
    ยังไม่มีบัญชี? · No account?
    <a href="{{ url_for('auth.register') }}">สมัครสมาชิก / Register</a>
  </p>
</section>
{% endblock %}
```


## `luma-webapp/app/templates/auth/register.html`

```html
{% extends "base.html" %}
{% block content %}
<section class="auth-card">
  <h1>สมัครสมาชิก / Register</h1>
  <p class="auth-subtitle">สร้างบัญชีเพื่อใช้ LUMA · Create your LUMA account</p>

  {% if errors.general %}
    <p class="field-error field-error-general">{{ errors.general }}</p>
  {% endif %}

  <form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

    <div class="form-group">
      <label for="username">ชื่อผู้ใช้ / Username</label>
      <input
        type="text"
        id="username"
        name="username"
        placeholder="your_username"
        required
        autocomplete="username"
        minlength="3"
        maxlength="80"
        value="{{ username or '' }}"
        class="{{ 'input-error' if errors.username }}"
      >
      {% if errors.username %}<p class="field-error">{{ errors.username }}</p>{% endif %}
    </div>

    <div class="form-group">
      <label for="email">อีเมล / Email</label>
      <input
        type="email"
        id="email"
        name="email"
        placeholder="you@example.com"
        required
        autocomplete="email"
        value="{{ email or '' }}"
        class="{{ 'input-error' if errors.email }}"
      >
      {% if errors.email %}<p class="field-error">{{ errors.email }}</p>{% endif %}
    </div>

    <div class="form-group">
      <label for="password">รหัสผ่าน / Password</label>
      <input
        type="password"
        id="password"
        name="password"
        placeholder="••••••••"
        required
        autocomplete="new-password"
        minlength="8"
        class="{{ 'input-error' if errors.password }}"
      >
      {% if errors.password %}<p class="field-error">{{ errors.password }}</p>{% endif %}
    </div>

    <button type="submit" id="register-btn">สมัครสมาชิก / Create Account</button>
  </form>

  <p class="auth-link">
    มีบัญชีแล้ว? · Already have an account?
    <a href="{{ url_for('auth.login') }}">เข้าสู่ระบบ / Login</a>
  </p>
</section>
{% endblock %}
```


## `luma-webapp/app/utils/__init__.py`

```python
# app/utils/__init__.py
```


## `luma-webapp/app/utils/logger.py`

```python
"""
app/utils/logger.py — Logging Configuration
--------------------------------------------
Input   : ชื่อ module ที่ต้องการ log
Process : สร้าง logger พร้อม format มาตรฐาน
Output  : Logger object

การใช้งาน:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("message")
    logger.error("error message")
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app=None):
    """
    ตั้งค่า logging สำหรับทั้งแอป
    เรียกครั้งเดียวใน create_app() ใน __init__.py
    """
    log_level = logging.DEBUG if (app and app.debug) else logging.INFO

    # Format: เวลา [ระดับ] ชื่อ module: ข้อความ
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # Console handler (แสดงใน terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    console_handler.setLevel(log_level)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # ลบ handler เดิมก่อน (ป้องกัน duplicate)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    # File handler (optional — เก็บ log ไว้อ่านทีหลัง)
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "luma.log"),
        maxBytes=1_000_000,   # 1 MB
        backupCount=3,
    )
    file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    file_handler.setLevel(logging.WARNING)  # เก็บเฉพาะ WARNING+ ใน file
    root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    สร้าง logger สำหรับ module ที่ระบุ
    ใช้ใน routes หรือ utils ต่าง ๆ
    """
    return logging.getLogger(name)
```


## `luma-webapp/instance/config.py.example`

```python
SECRET_KEY = "change-this-to-a-random-secret-key"
SQLALCHEMY_DATABASE_URI = "sqlite:///luma.db"
FORGE_AI_ENDPOINT = "http://localhost:7860"
```


## `luma-webapp/instance/luma.db`

> ไฟล์ binary (24,576 bytes) — ไม่ฝังเนื้อหาลงเอกสาร

> **หมายเหตุสำคัญ**: ไฟล์นี้เคยถูก commit ขึ้น git ทั้งที่ `.gitignore` มีบรรทัด `instance/*.db` อยู่แล้ว (ถูก commit ก่อนที่จะเพิ่มกฎ ignore) และเป็นต้นเหตุที่ `test_system_check.py` ล้ม 3 ข้อ เพราะ schema ในไฟล์เก่า ไม่มีคอลัมน์ `users.avatar_url`, `users.last_login_at`, `jobs.prompt` ที่ PR #12 เพิ่มเข้ามา และ `db.create_all()` ไม่ ALTER ตารางที่มีอยู่แล้ว


## `luma-webapp/tests/__init__.py`

```python

```


## `luma-webapp/tests/conftest.py`

```python
"""
tests/conftest.py — fixtures ที่ทุก test ไฟล์ใช้ร่วมกัน
--------------------------------------------------------
รวมจาก 2 branch ที่แยกกันตาม issue (feature/backend-auth-issue2-3 Issue #2/#3 และ
feature/forge-ai-issue5-6 Issue #5/#6) — ทั้งสองฝั่งเขียน fixture ชุดเดียวกันไว้
โดยตั้งใจ ตอน merge จึงใช้ superset ตามที่คอมเมนต์ในทั้งสองไฟล์ระบุไว้

  app     : Flask app instance ที่ config ใหม่สำหรับ test โดยเฉพาะ (in-memory
            SQLite, ปิด CSRF, ไม่ต้องมี instance/config.py ในเครื่อง)
  client  : Flask test client — เรียก route ได้เหมือน HTTP request จริงแต่ไม่ต้องรัน server
  mock_forge_success : patch requests.post ให้ตอบเหมือน Forge AI ส่ง PNG กลับมาสำเร็จ
"""

import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# ให้ `from app import ...` ทำงานได้แม้รัน pytest จาก repo root ไม่ใช่จาก luma-webapp/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db  # noqa: E402  (ต้องมาหลัง sys.path.insert)

# 1x1 red PNG — เหมือนตัวที่ใช้ตอนทดสอบ manual ด้วย mock server
TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


@pytest.fixture()
def app():
    test_app = create_app(config_overrides={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key-not-for-real-use",
        "WTF_CSRF_ENABLED": False,  # ปิดเฉพาะตอน test — CSRFProtect ยังทำงานจริงตอน run.py
    })
    yield test_app
    with test_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def mock_forge_success():
    """จำลอง Forge AI ตอบกลับสำเร็จพร้อมรูป 1x1 PNG — ไม่ต้องมี Stable Diffusion WebUI จริง"""
    with patch("app.routes.api.requests.post") as mock_post:
        response = MagicMock()
        response.json.return_value = {"images": [TINY_PNG_B64]}
        mock_post.return_value = response  # .raise_for_status() no-ops on a bare MagicMock
        yield mock_post


def register(client, username="tester1", email="tester1@example.com", password="password123"):
    return client.post("/auth/register", data={
        "username": username, "email": email, "password": password,
    }, follow_redirects=True)


def login(client, email="tester1@example.com", password="password123"):
    return client.post("/auth/login", data={
        "email": email, "password": password,
    })


def register_and_login(client, username="tester1", email="tester1@example.com", password="password123"):
    register(client, username, email, password)
    return login(client, email, password)
```


## `luma-webapp/tests/test_assets.py`

```python
"""
tests/test_assets.py — ownership / IDOR regression tests (F05)

Delete-endpoint tests (Issue #3) live in the feature/backend-auth-issue2-3
branch's own test_assets_delete.py, next to the endpoint itself — that
endpoint isn't part of this branch.
"""

from tests.conftest import register, login, register_and_login


def _generate(client, prompt="idor test"):
    resp = client.post("/api/generate", json={"prompt": prompt})
    assert resp.status_code == 200
    return resp.get_json()


def test_image_requires_login(client, mock_forge_success):
    register_and_login(client)
    asset = _generate(client)
    client.post("/auth/logout")

    resp = client.get(asset["image_url"])
    assert resp.status_code == 401


def test_image_owner_can_view(client, mock_forge_success):
    register_and_login(client)
    asset = _generate(client)
    resp = client.get(asset["image_url"])
    assert resp.status_code == 200


def test_image_non_owner_gets_404_not_someone_elses_image(client, mock_forge_success):
    register_and_login(client, username="owner", email="owner@example.com")
    asset = _generate(client)
    client.post("/auth/logout")

    register(client, username="intruder", email="intruder@example.com")
    login(client, email="intruder@example.com")

    resp = client.get(asset["image_url"])
    assert resp.status_code == 404
```


## `luma-webapp/tests/test_assets_delete.py`

```python
"""
tests/test_assets_delete.py — Issue #3: DELETE /api/assets/<id>
"""

from tests.conftest import register, login, register_and_login


def _generate(client, prompt="delete test"):
    resp = client.post("/api/generate", json={"prompt": prompt})
    assert resp.status_code == 200
    return resp.get_json()


def test_delete_requires_login(client, mock_forge_success):
    register_and_login(client)
    asset = _generate(client)
    client.post("/auth/logout")

    resp = client.delete(f"/api/assets/{asset['asset_id']}")
    assert resp.status_code == 401


def test_delete_requires_ownership(client, mock_forge_success):
    register_and_login(client, username="owner", email="owner@example.com")
    asset = _generate(client)
    client.post("/auth/logout")

    register(client, username="intruder", email="intruder@example.com")
    login(client, email="intruder@example.com")

    resp = client.delete(f"/api/assets/{asset['asset_id']}")
    assert resp.status_code == 404

    # still there for the real owner afterward — must log out the intruder
    # first, since login() no-ops while a session is already authenticated
    client.post("/auth/logout")
    login(client, email="owner@example.com")
    resp = client.get(asset["image_url"])
    assert resp.status_code == 200


def test_delete_removes_asset_and_is_idempotent_safe(client, mock_forge_success):
    register_and_login(client)
    asset = _generate(client)

    resp = client.delete(f"/api/assets/{asset['asset_id']}")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "deleted", "asset_id": asset["asset_id"]}

    resp = client.get(asset["image_url"])
    assert resp.status_code == 404

    resp = client.get("/api/assets")
    assert resp.get_json() == []

    # deleting again must not 500
    resp = client.delete(f"/api/assets/{asset['asset_id']}")
    assert resp.status_code == 404


def test_delete_nonexistent_asset_is_404(client):
    register_and_login(client)
    resp = client.delete("/api/assets/9999")
    assert resp.status_code == 404
```


## `luma-webapp/tests/test_auth.py`

```python
"""
tests/test_auth.py — regression tests for the auth fixes from the security review
(open redirect, account enumeration, password policy, rate limiting, crash-on-missing-field)
"""

from tests.conftest import register, login, register_and_login


def test_duplicate_username_and_email_rejected(client):
    register(client, username="dupe", email="dupe@example.com")
    resp = register(client, username="dupe", email="someoneelse@example.com")
    assert "ไม่สามารถ".encode() in resp.data


def test_weak_password_rejected_server_side(client):
    resp = client.post("/auth/register", data={
        "username": "weakpw", "email": "weakpw@example.com", "password": "a",
    })
    assert resp.status_code == 200  # re-renders the form with a field error, not a redirect
    assert b"8" in resp.data  # mentions the minimum length


def test_login_wrong_password_no_crash(client):
    register(client, username="u1", email="u1@example.com")
    resp = login(client, email="u1@example.com", password="wrongpassword")
    assert resp.status_code == 200


def test_login_missing_fields_does_not_500(client):
    # regression test for F03: request.form["email"] used to raise an
    # unhandled BadRequestKeyError (500) when the field was simply absent
    resp = client.post("/auth/login", data={})
    assert resp.status_code == 200


def test_open_redirect_blocked(client):
    register(client, username="u2", email="u2@example.com")
    resp = client.post(
        "/auth/login?next=https://evil.example/steal",
        data={"email": "u2@example.com", "password": "password123"},
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/dashboard"


def test_open_redirect_allows_safe_relative_path(client):
    register(client, username="u3", email="u3@example.com")
    resp = client.post(
        "/auth/login?next=/api/assets",
        data={"email": "u3@example.com", "password": "password123"},
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/api/assets"


def test_login_rate_limited_after_repeated_failures(client):
    register(client, username="u4", email="u4@example.com")
    for _ in range(5):
        login(client, email="u4@example.com", password="wrongpassword")
    resp = login(client, email="u4@example.com", password="wrongpassword")
    assert resp.status_code == 429


def test_rate_limit_does_not_block_a_different_account(client):
    register(client, username="target", email="target@example.com")
    register(client, username="bystander", email="bystander@example.com")
    for _ in range(5):
        login(client, email="target@example.com", password="wrongpassword")
    # target is now rate-limited, but an unrelated account must still work
    resp = login(client, email="bystander@example.com", password="password123")
    assert resp.status_code == 302


def test_logout_requires_post(client):
    register_and_login(client)
    resp = client.get("/auth/logout")
    assert resp.status_code == 405  # GET is no longer allowed


def test_logout_post_ends_session(client):
    register_and_login(client)
    client.post("/auth/logout")
    resp = client.get("/dashboard")
    assert resp.status_code == 302
```


## `luma-webapp/tests/test_e2e_flow.py`

```python
"""
tests/test_e2e_flow.py — Issue #6: full flow register -> login -> generate -> view image
"""

from tests.conftest import register, login, register_and_login


def test_full_flow_register_login_generate_view_image(client, mock_forge_success):
    # 1) register
    resp = register(client)
    assert resp.status_code == 200  # followed the redirect to the login page

    # 2) login
    resp = login(client)
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/dashboard"

    # 3) generate
    resp = client.post("/api/generate", json={"prompt": "a cat wizard, digital art"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "success"
    assert "asset_id" in body
    assert body["image_url"] == f"/api/assets/{body['asset_id']}/image"
    mock_forge_success.assert_called_once()

    # 4) view the generated image
    resp = client.get(body["image_url"])
    assert resp.status_code == 200
    assert resp.content_type == "image/png"

    # gallery reflects the new asset with its prompt
    resp = client.get("/api/assets")
    assert resp.status_code == 200
    assets = resp.get_json()
    assert len(assets) == 1
    assert assets[0]["prompt"] == "a cat wizard, digital art"


def test_dashboard_requires_login(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]


def test_dashboard_reachable_after_login(client):
    register_and_login(client)
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"tester1" in resp.data
```


## `luma-webapp/tests/test_generate_params.py`

```python
"""
tests/test_generate_params.py — Issue #5: extended generate parameters + validation
"""

from tests.conftest import register_and_login


def test_prompt_required(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={})
    assert resp.status_code == 400


def test_non_string_prompt_rejected_not_500(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": 12345})
    assert resp.status_code == 400


def test_default_params_used_when_omitted(client, mock_forge_success):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": "a cat"})
    assert resp.status_code == 200
    sent = mock_forge_success.call_args.kwargs["json"]
    assert sent["steps"] == 20
    assert sent["cfg_scale"] == 7
    assert sent["width"] == 512
    assert sent["height"] == 512
    assert sent["negative_prompt"] == ""


def test_extended_params_forwarded_to_forge(client, mock_forge_success):
    register_and_login(client)
    resp = client.post("/api/generate", json={
        "prompt": "a cat",
        "negative_prompt": "blurry, low quality",
        "steps": 35,
        "cfg_scale": 9.5,
        "width": 1024,
        "height": 768,
    })
    assert resp.status_code == 200
    sent = mock_forge_success.call_args.kwargs["json"]
    assert sent["negative_prompt"] == "blurry, low quality"
    assert sent["steps"] == 35
    assert sent["cfg_scale"] == 9.5
    assert sent["width"] == 1024
    assert sent["height"] == 768


def test_steps_over_max_rejected(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": "a cat", "steps": 999})
    assert resp.status_code == 400


def test_steps_must_be_integer(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": "a cat", "steps": "twenty"})
    assert resp.status_code == 400


def test_cfg_scale_out_of_range_rejected(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": "a cat", "cfg_scale": 500})
    assert resp.status_code == 400


def test_width_must_be_an_allowed_value(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": "a cat", "width": 999})
    assert resp.status_code == 400


def test_height_must_be_an_allowed_value(client):
    register_and_login(client)
    resp = client.post("/api/generate", json={"prompt": "a cat", "height": 100})
    assert resp.status_code == 400
```


## `luma-webapp/tests/test_models.py`

```python
"""
tests/test_models.py — Issue #2: extended DB models
"""

from app import db
from app.models import User, Asset, Job


def test_user_new_fields_default_to_none(app):
    with app.app_context():
        user = User(username="u", email="u@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        assert user.avatar_url is None
        assert user.last_login_at is None
        assert repr(user) == f"<User id={user.id} username='u'>"


def test_login_sets_last_login_at(client):
    from tests.conftest import register, login

    register(client, username="u2", email="u2@example.com")
    login(client, email="u2@example.com")

    with client.application.app_context():
        user = User.query.filter_by(username="u2").first()
        assert user.last_login_at is not None


def test_job_has_prompt_and_asset_relationship(app):
    with app.app_context():
        user = User(username="u3", email="u3@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        asset = Asset(user_id=user.id, filename="a.png", prompt="a cat")
        db.session.add(asset)
        db.session.commit()

        job = Job(user_id=user.id, prompt="a cat", status="done", result_asset_id=asset.id)
        db.session.add(job)
        db.session.commit()

        assert job.prompt == "a cat"
        assert job.result_asset.id == asset.id
        assert repr(job) == f"<Job id={job.id} user_id={user.id} status='done'>"
        assert repr(asset) == f"<Asset id={asset.id} user_id={user.id} filename='a.png'>"
```


## `luma-webapp/tests/test_system_check.py`

```python
"""
Test script — ตรวจสอบว่าโปรเจค LUMA ใช้ได้จริงทุกส่วน
"""
import sys
import os

# ต้องรันจาก luma-webapp/ directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PASS = 0
FAIL = 0

def check(label, fn):
    global PASS, FAIL
    try:
        fn()
        print(f"  [PASS] {label}")
        PASS += 1
    except Exception as e:
        print(f"  [FAIL] {label}: {e}")
        FAIL += 1

print("=" * 55)
print("  LUMA Web App — System Check")
print("=" * 55)

# 1) Imports
print("\n[1] Import check")
check("flask importable",            lambda: __import__("flask"))
check("flask_sqlalchemy importable", lambda: __import__("flask_sqlalchemy"))
check("flask_login importable",      lambda: __import__("flask_login"))
check("flask_migrate importable",    lambda: __import__("flask_migrate"))
check("requests importable",         lambda: __import__("requests"))
check("werkzeug importable",         lambda: __import__("werkzeug"))

# 2) create_app
print("\n[2] Application Factory")
from app import create_app, db
app = create_app()
check("create_app() returns app",    lambda: app is not None)

# 3) Routes registered
print("\n[3] Blueprint routes")
rules = [str(r) for r in app.url_map.iter_rules()]
check("/ exists",                    lambda: "/" in rules)
check("/dashboard exists",           lambda: "/dashboard" in rules)
check("/auth/login exists",          lambda: "/auth/login" in rules)
check("/auth/register exists",       lambda: "/auth/register" in rules)
check("/auth/logout exists",         lambda: "/auth/logout" in rules)
check("/api/generate exists",        lambda: "/api/generate" in rules)
check("/api/assets exists",          lambda: "/api/assets" in rules)

# 4) Database
print("\n[4] Database (SQLite)")
from app.models import User, Asset, Job
with app.app_context():
    check("tables created",          lambda: db.session.execute(db.select(User)).scalars().all() is not None)
    check("Asset query ok",          lambda: db.session.execute(db.select(Asset)).scalars().all() is not None)
    check("Job query ok",            lambda: db.session.execute(db.select(Job)).scalars().all() is not None)
    check("db.session.get() works",  lambda: db.session.get(User, 999) is None)

# 5) Auth logic
print("\n[5] Auth model logic")
u = User(username="testuser", email="test@test.com")
u.set_password("password123")
check("password hash stored",        lambda: u.password_hash != "password123")
check("check_password correct",      lambda: u.check_password("password123"))
check("check_password wrong rejects",lambda: not u.check_password("wrongpass"))

# 6) Logger
print("\n[6] Utils / Logger")
from app.utils.logger import get_logger, setup_logging
check("get_logger() callable",       lambda: get_logger("test") is not None)
check("setup_logging() callable",    lambda: setup_logging(app) is None)

# 7) Config keys
print("\n[7] Config keys")
with app.app_context():
    from flask import current_app
    check("SECRET_KEY set",              lambda: bool(current_app.config.get("SECRET_KEY")))
    check("SQLALCHEMY_DATABASE_URI set", lambda: bool(current_app.config.get("SQLALCHEMY_DATABASE_URI")))
    check("FORGE_AI_ENDPOINT set",       lambda: bool(current_app.config.get("FORGE_AI_ENDPOINT")))

# Summary
print("\n" + "=" * 55)
print(f"  Result: {PASS} passed, {FAIL} failed")
print("=" * 55)


def test_all_checks_passed():
    """pytest entry point — fails the suite if any manual check above failed."""
    assert FAIL == 0, f"{FAIL} system check(s) failed — see output above"
```
