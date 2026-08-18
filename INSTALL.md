# คู่มือติดตั้ง LUMA

รองรับ **Windows** · **macOS** (Intel + Apple Silicon) · **Linux** · **Conda**

> ทุกเวอร์ชันใน `requirements.txt` ถูก **ล็อกไว้** และ**ทดสอบร่วมกันแล้ว** บน Python 3.12
> — backend `pytest` 33/33 ผ่าน · ai-engine smoke test 31/31 ผ่าน
> ล็อกไว้เพื่อให้ทุกคนในทีมได้ environment เดียวกัน ไม่เกิดปัญหา "เครื่องผมรันได้"

---

## สารบัญ

1. [ต้องมีอะไรก่อน](#1-ต้องมีอะไรก่อน)
2. [เลือกวิธีติดตั้ง](#2-เลือกวิธีติดตั้ง)
3. [วิธีที่ 1 — venv + pip (Windows)](#3-วิธีที่-1--venv--pip-windows)
4. [วิธีที่ 2 — venv + pip (macOS / Linux)](#4-วิธีที่-2--venv--pip-macos--linux)
5. [วิธีที่ 3 — Conda](#5-วิธีที่-3--conda)
6. [ติดตั้งแบบแยกเครื่อง (3 เครื่องตามสเปกอาจารย์)](#6-ติดตั้งแบบแยกเครื่อง-3-เครื่องตามสเปกอาจารย์)
7. [ตั้งค่า config](#7-ตั้งค่า-config)
8. [ตรวจว่าติดตั้งสำเร็จ](#8-ตรวจว่าติดตั้งสำเร็จ)
9. [รันโปรเจกต์](#9-รันโปรเจกต์)
10. [แก้ปัญหาที่เจอบ่อย](#10-แก้ปัญหาที่เจอบ่อย)

---

## 1. ต้องมีอะไรก่อน

| ของ | เวอร์ชัน | หมายเหตุ |
|---|---|---|
| **Python** | **3.12** (แนะนำ) | ทุก dependency ทดสอบบน 3.12 · 3.11 และ 3.13 น่าจะใช้ได้แต่ยังไม่ได้ทดสอบ |
| **Git** | อะไรก็ได้ | |
| Conda | ถ้าใช้วิธีที่ 3 | Miniconda พอ ไม่ต้อง Anaconda เต็ม |
| **Stable Diffusion WebUI (Forge)** | — | **เฉพาะเครื่อง AI** ติดตั้งแยกผ่าน Stability Matrix ไม่เกี่ยวกับ `requirements.txt` |

### เช็คว่ามี Python แล้วหรือยัง

**Windows (PowerShell)**
```powershell
py --list          # ดูว่ามี Python เวอร์ชันไหนในเครื่อง
py -3.12 --version
```

**macOS / Linux**
```bash
python3 --version
```

### ถ้ายังไม่มี Python

| ระบบ | วิธีติดตั้ง |
|---|---|
| **Windows** | ดาวน์โหลดจาก [python.org](https://www.python.org/downloads/) · ⚠️ ติ๊ก **"Add python.exe to PATH"** ตอนติดตั้ง |
| **macOS** | `brew install python@3.12` (ถ้ายังไม่มี Homebrew: [brew.sh](https://brew.sh)) |
| **Linux (Debian/Ubuntu)** | `sudo apt install python3.12 python3.12-venv` |

---

## 2. เลือกวิธีติดตั้ง

| ถ้าคุณ... | ใช้วิธี |
|---|---|
| ใช้ Windows และไม่มี Conda | **วิธีที่ 1** |
| ใช้ Mac หรือ Linux | **วิธีที่ 2** |
| มี Conda อยู่แล้ว / ชอบ Conda | **วิธีที่ 3** |
| จะ deploy จริงแยก 3 เครื่อง | **หัวข้อ 6** |

> ทำงานคนเดียวบนเครื่องเดียว → ติดตั้ง `requirements-dev.txt` ที่รวมทุก service
> ทำงานตามบทบาทบนเครื่องแยก → ติดตั้งแค่ service ของตัวเอง (หัวข้อ 6)

---

## 3. วิธีที่ 1 — venv + pip (Windows)

```powershell
# 1) clone
git clone https://github.com/boss2912/luma-webapp-g04.git
cd luma-webapp-g04

# 2) สร้าง virtual environment
py -3.12 -m venv .venv

# 3) activate
.\.venv\Scripts\Activate.ps1

# 4) อัปเดต pip ก่อน (กัน error แปลกๆ)
python -m pip install --upgrade pip

# 5) ติดตั้งทุก service (สำหรับ dev บนเครื่องเดียว)
pip install -r requirements-dev.txt
```

### ถ้า `Activate.ps1` ขึ้น error เรื่อง execution policy

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
แล้ว activate ใหม่ · หรือใช้ `cmd` แทน: `.\.venv\Scripts\activate.bat`

### ตรวจว่าติดตั้งถูกจริง

```bash
python tools/check_env_installed.py
```

บอกทันทีว่าขาดอะไร เวอร์ชันไหนไม่ตรง และเวอร์ชัน Python ถูกหรือเปล่า
**ควรรันทุกครั้งหลังตั้งเครื่องเสร็จ** — เคยมีกรณี env ที่ดูเหมือนใช้ได้
แต่จริงๆ เป็น Python คนละเวอร์ชันและ package ไม่ตรง 11 จาก 16 ตัว

ถ้าลงเฉพาะ service เดียว (แบบ 3 เครื่องในหัวข้อ 6) บอกด้วยว่าเครื่องนี้ทำหน้าที่อะไร:

```bash
python tools/check_env_installed.py --profile backend
python tools/check_env_installed.py --profile database
python tools/check_env_installed.py --profile ai-engine
```

### ออกจาก venv
```powershell
deactivate
```

---

## 4. วิธีที่ 2 — venv + pip (macOS / Linux)

```bash
# 1) clone
git clone https://github.com/boss2912/luma-webapp-g04.git
cd luma-webapp-g04

# 2) สร้าง virtual environment
python3.12 -m venv .venv
# ถ้าไม่มี python3.12 ใช้ python3 ธรรมดาได้ แต่เช็คก่อนว่าเป็น 3.11+
#   python3 --version

# 3) activate
source .venv/bin/activate

# 4) อัปเดต pip
python -m pip install --upgrade pip

# 5) ติดตั้งทุก service
pip install -r requirements-dev.txt
```

### หมายเหตุสำหรับ Mac

**Apple Silicon (M1/M2/M3/M4)** — `opencv-python`, `numpy`, `scipy`, `scikit-image`
มี wheel สำหรับ arm64 ครบแล้ว ติดตั้งได้ตรงๆ ไม่ต้อง compile และไม่ต้องใช้ Rosetta

**ถ้า `matplotlib` เปิดหน้าต่างไม่ได้** — บน Mac ปกติใช้ได้เลย แต่ถ้ารันบน server
หรือใน SSH ให้ตั้ง backend เป็น `Agg` ก่อน import `pyplot`:
```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
```

**`cv.imshow()` บน Mac** — ต้องรันจาก terminal ปกติ (ไม่ใช่ผ่าน SSH)
ถ้ามีปัญหาให้ `cv.imwrite()` เป็นไฟล์แล้วเปิดดูแทน — ในโปรเจกต์นี้เราเซฟไฟล์อยู่แล้ว
เพราะต้องเอาไปใส่รายงาน

### ตรวจว่าติดตั้งถูกจริง

```bash
python tools/check_env_installed.py
```

บอกทันทีว่าขาดอะไร เวอร์ชันไหนไม่ตรง และเวอร์ชัน Python ถูกหรือเปล่า
**ควรรันทุกครั้งหลังตั้งเครื่องเสร็จ** — เคยมีกรณี env ที่ดูเหมือนใช้ได้
แต่จริงๆ เป็น Python คนละเวอร์ชันและ package ไม่ตรง 11 จาก 16 ตัว

ถ้าลงเฉพาะ service เดียว (แบบ 3 เครื่องในหัวข้อ 6) บอกด้วยว่าเครื่องนี้ทำหน้าที่อะไร:

```bash
python tools/check_env_installed.py --profile backend
python tools/check_env_installed.py --profile database
python tools/check_env_installed.py --profile ai-engine
```

### ออกจาก venv
```bash
deactivate
```

---

## 5. วิธีที่ 3 — Conda

ใช้ได้เหมือนกันทั้ง Windows / macOS / Linux

```bash
# 1) clone
git clone https://github.com/boss2912/luma-webapp-g04.git
cd luma-webapp-g04

# 2) สร้าง environment จาก environment.yml
conda env create -f environment.yml

# 3) activate
conda activate luma
```

### คำสั่ง Conda ที่ใช้บ่อย

```bash
conda activate luma                              # เข้า env
conda deactivate                                 # ออก
conda env update -f environment.yml --prune      # อัปเดตเมื่อ environment.yml เปลี่ยน
conda env list                                   # ดู env ทั้งหมด
conda env remove -n luma                         # ลบ env ทิ้ง (ถ้าพัง สร้างใหม่ได้)
```

### ทำไม `environment.yml` ลง library ผ่าน `pip:` ไม่ใช่ conda ตรงๆ

เพื่อให้เวอร์ชัน**ตรงกับ `requirements.txt` เป๊ะ** — package เดียวกันบน conda-forge
มี build number ต่างกันและมักเป็นเวอร์ชันคนละตัว ถ้าลงผ่าน conda จะค่อยๆ เพี้ยน
ไปจากชุดที่ทดสอบไว้ เอาเฉพาะ `python` กับ `pip` จาก conda ก็พอ

### ถ้าอยาก env แบบสลิม (เฉพาะ service ที่ต้องใช้)

```bash
conda create -n luma-backend python=3.12 pip
conda activate luma-backend
pip install -r services/backend/requirements.txt
```

---

### ตรวจว่าติดตั้งถูกจริง

```bash
python tools/check_env_installed.py
```

บอกทันทีว่าขาดอะไร เวอร์ชันไหนไม่ตรง และเวอร์ชัน Python ถูกหรือเปล่า
**ควรรันทุกครั้งหลังตั้งเครื่องเสร็จ** — เคยมีกรณี env ที่ดูเหมือนใช้ได้
แต่จริงๆ เป็น Python คนละเวอร์ชันและ package ไม่ตรง 11 จาก 16 ตัว

ถ้าลงเฉพาะ service เดียว (แบบ 3 เครื่องในหัวข้อ 6) บอกด้วยว่าเครื่องนี้ทำหน้าที่อะไร:

```bash
python tools/check_env_installed.py --profile backend
python tools/check_env_installed.py --profile database
python tools/check_env_installed.py --profile ai-engine
```

---

## 6. ติดตั้งแบบแยกเครื่อง (3 เครื่องตามสเปกอาจารย์)

ตาม Lecture 4 หน้า 56 — **ลงเฉพาะที่เครื่องนั้นต้องใช้** ไม่ต้องลงทุกอย่างทุกเครื่อง

| เครื่อง | บทบาท | คำสั่งติดตั้ง |
|---|---|---|
| **192.168.1.10** | Frontend + Nginx | **ไม่ต้องลง Python package เลย** — เป็น HTML/CSS/JS ล้วน |
| **192.168.1.20** | Flask backend + SQLite | `pip install -r services/backend/requirements.txt`<br>`pip install -r services/database/requirements.txt` |
| **192.168.1.30** | Forge AI + Image Processing (GPU) | `pip install -r services/ai-engine/requirements.txt` |

> เครื่อง frontend ไม่ต้องลง OpenCV · เครื่อง backend ไม่ต้องลง matplotlib
> ประหยัดเวลาและพื้นที่มาก

### เครื่อง Frontend เสิร์ฟไฟล์อย่างไร

**ตอน dev** — ใช้ web server ที่ติดมากับ Python ได้เลย ไม่ต้องลงอะไร:
```bash
cd services/frontend
python -m http.server 8080
```

**ตอน V5** — Nginx เสิร์ฟให้ (ดู `deploy/nginx/`)

### เครื่อง AI ต้องมี Stable Diffusion WebUI ด้วย

`requirements.txt` ของ `ai-engine` **ไม่มี** `torch` / `diffusers` เพราะ
Stable Diffusion WebUI (Forge) เป็นโปรแกรมแยกที่มี environment ของตัวเอง
ติดตั้งผ่าน **Stability Matrix** และ service ของเราคุยกับมันผ่าน HTTP เท่านั้น

ถ้าใส่ `torch` เข้าไปจะโหลดหลาย GB ฟรีๆ โดยไม่ได้ใช้

---

## 7. ตั้งค่า config

ไฟล์ config จริง **ไม่อยู่ใน git** เพราะมี `SECRET_KEY`
(v1 เคยหลุดขึ้น GitHub — ดู `archive/SECURITY_FIXES_v1.md` F09)

```bash
# คัดลอกจาก template
cp services/backend/instance/config.py.example services/backend/instance/config.py
```
Windows PowerShell:
```powershell
Copy-Item services\backend\instance\config.py.example services\backend\instance\config.py
```

แล้วแก้ค่าในไฟล์:

```python
SECRET_KEY = "ใส่ค่าสุ่มของตัวเอง-ห้ามใช้ค่า default"
SQLALCHEMY_DATABASE_URI = "sqlite:///luma.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# ชี้ไปที่เครื่อง AI จริง - ห้าม hardcode localhost ตอน deploy หลายเครื่อง
FORGE_AI_ENDPOINT = "http://192.168.1.30:7860/sdapi/v1/txt2img"
AI_ENGINE_URL     = "http://192.168.1.30:8000"
```

### สร้าง SECRET_KEY แบบสุ่ม

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 8. ตรวจว่าติดตั้งสำเร็จ

```bash
python -c "import flask, flask_sqlalchemy, flask_login, flask_migrate, flask_wtf; print('backend OK')"
python -c "import cv2, numpy, skimage, matplotlib, scipy, PIL; print('ai-engine OK')"
python -c "import sqlalchemy, alembic; print('database OK')"
python -m pytest --version
```

เช็คเวอร์ชันว่าตรงกับที่ล็อกไว้:
```bash
python -c "import cv2, numpy; print('opencv', cv2.__version__, '| numpy', numpy.__version__)"
# ควรได้: opencv 5.0.0 | numpy 2.5.2
```

### ✅ วิธีที่ดีที่สุด — รัน smoke test ที่เตรียมไว้

```bash
# ตรวจ ai-engine: เรียก 31 operation ที่ pipeline 5 ส่วนต้องใช้จริงกับภาพทดสอบ
python tools/smoke_test_ai_deps.py

# ตรวจว่า requirements ทุกไฟล์เป็น ASCII (กันบั๊ก locale ไทย)
python tools/check_requirements_ascii.py
```

ควรได้ `31 passed, 0 failed` และ `requirements ทั้ง 4 ไฟล์เป็น ASCII ล้วน`

สคริปต์นี้ไม่ได้เช็คแค่ว่า import ผ่าน แต่เรียกใช้จริง — `imread` · `cvtColor` HSV ·
`filter2D` · `sepFilter2D` · `medianBlur` · `equalizeHist` · gamma LUT · `dft`/`idft` ·
`morphologyEx` · Otsu · `findContours` · `Canny` · alpha merge · skew/kurtosis ·
PSNR · SSIM · IoU · matplotlib headless savefig · PIL interop

### รัน test ของแต่ละ service

```bash
python -m pytest services/backend/tests -q
python -m pytest services/ai-engine/tests -q
python -m pytest services/database/tests -q
```

> ตอนนี้โฟลเดอร์ `tests/` ยังว่างอยู่ (โปรเจกต์เพิ่งวางโครง)
> pytest จะบอกว่า "no tests ran" — ถือว่าปกติ

---

## 9. รันโปรเจกต์

> ⚠️ ยังไม่มีโค้ดให้รันครับ โปรเจกต์อยู่ในช่วงวางโครงสร้าง
> หัวข้อนี้เป็นรูปแบบคำสั่งที่จะใช้เมื่อ V2 เริ่มมีของ — ดู `docs/ROADMAP.md`

### Backend

```bash
cd services/backend
python run.py
```
เปิด http://127.0.0.1:5000

### Environment variable ที่คุม backend

| ตัวแปร | default | ความหมาย |
|---|---|---|
| `LUMA_DEBUG` | `0` | `1` = เปิด debug mode + auto-reload |
| `LUMA_HOST` | `127.0.0.1` | `0.0.0.0` = ให้เครื่องอื่นบน LAN เข้าถึงได้ |

**Windows PowerShell**
```powershell
$env:LUMA_DEBUG = "1"
python run.py
```

**macOS / Linux**
```bash
LUMA_DEBUG=1 python run.py
```

**ตอนต่อข้ามเครื่องจริง** (ให้เครื่อง frontend เรียกได้)
```bash
LUMA_HOST=0.0.0.0 python run.py
```

### 🔴 ห้ามเปิด `LUMA_DEBUG=1` พร้อม `LUMA_HOST=0.0.0.0`

Werkzeug debugger **รันโค้ด Python จากหน้าเว็บได้** เมื่อเจอ exception
พอ bind ทุก interface = **ทุกเครื่องบน network ยึดเครื่องคุณได้** โดยไม่มีรหัสผ่านกั้น

v1 เคย hardcode ทั้งสองอย่างไว้พร้อมกัน (ช่องโหว่ F02) — อย่าให้ซ้ำ

---

## 10. แก้ปัญหาที่เจอบ่อย

### ❌ `UnicodeDecodeError` ตอน `pip install -r`

```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 887
decoding with 'cp874' codec failed
```

**สาเหตุ**: pip อ่านไฟล์ requirements ด้วย codec ของ locale เครื่อง — บน Windows
ภาษาไทยคือ `cp874` ถ้าไฟล์เป็น UTF-8 ที่มีตัวอักษรไทยจะพัง

**ในโปรเจกต์นี้แก้ไว้แล้ว** — `requirements.txt` ทุกไฟล์เป็น **ASCII ล้วน**
คำอธิบายภาษาไทยอยู่ในไฟล์นี้แทน (ทดสอบแล้วว่าลงได้โดยไม่ต้องตั้งอะไรเพิ่ม)

**ถ้ายังเจอ** (เช่นแก้ไฟล์เองแล้วเผลอใส่ไทยเข้าไป):
```powershell
$env:PYTHONUTF8 = "1"        # Windows
```
```bash
export PYTHONUTF8=1          # macOS / Linux
```
แล้วเอาข้อความไทยออกจาก `requirements.txt`

---

### ❌ `ModuleNotFoundError: No module named 'cv2'`

ลืม activate venv หรือลง `requirements.txt` ผิด service

```bash
# เช็คว่าใช้ python ตัวไหน
python -c "import sys; print(sys.executable)"
```
ต้องชี้ไปที่ `.venv/` หรือ env ของ conda ไม่ใช่ Python ของระบบ

---

### ❌ `No module named pip`

venv สร้างไม่สมบูรณ์ หรือใช้ Python จาก venv อื่นอยู่ — สร้างใหม่:
```bash
rm -rf .venv          # Windows: Remove-Item -Recurse -Force .venv
python3.12 -m venv .venv
```

---

### ❌ `Activate.ps1 cannot be loaded because running scripts is disabled`

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

### ❌ Test ล้มด้วย `no such column: users.avatar_url`

ไฟล์ฐานข้อมูลเก่ามี schema ไม่ตรงกับ models
**`db.create_all()` ไม่ ALTER ตารางที่มีอยู่แล้ว** มันสร้างแค่ตารางที่ยังไม่มี

**แก้**: ลบไฟล์ `.db` แล้วรันใหม่
```bash
rm services/backend/instance/luma.db
```

**กันไม่ให้เกิดอีก**: ใช้ migration จริงเสมอ
```bash
flask db migrate -m "add column"
flask db upgrade
```

> นี่คือปัญหาจริงที่ v1 เจอ ทำให้ test ล้ม 3 ข้อ — ดู `archive/ARCHITECTURE_v1.md` ปัญหา A

---

### ❌ `ON DELETE CASCADE` ไม่ทำงานบน SQLite

SQLite ปิด foreign key เป็น **default** ต้องเปิดทุก connection:
```sql
PRAGMA foreign_keys = ON;
```

---

### ❌ `matplotlib` error บน server / SSH / Docker

ไม่มีหน้าจอให้วาด — ตั้ง backend เป็น `Agg` **ก่อน** import `pyplot`:
```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
```

---

### ❌ เชื่อมต่อ Forge AI ไม่ได้ (502)

1. Stable Diffusion WebUI เปิดอยู่จริงไหม
2. เปิดด้วย `--api` แล้วหรือยัง (ต้องมี flag นี้ API ถึงทำงาน)
3. `FORGE_AI_ENDPOINT` ใน config ชี้ IP ถูกไหม
4. firewall เครื่อง AI เปิดพอร์ต 7860 ให้เครื่องอื่นไหม

เช็คจากเครื่อง backend:
```bash
curl http://192.168.1.30:7860/sdapi/v1/sd-models
```

---

### ❌ เครื่องอื่นบน LAN เข้า backend ไม่ได้

1. รันด้วย `LUMA_HOST=0.0.0.0` แล้วหรือยัง
2. firewall เปิดพอร์ต 5000 ไหม
   ```powershell
   # Windows - รันแบบ Administrator
   New-NetFirewallRule -DisplayName "LUMA Flask" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
   ```
3. เครื่องอยู่วง LAN เดียวกันจริงไหม — `ping 192.168.1.20`

---

### ℹ️ `DeprecationWarning: datetime.utcnow() is deprecated`

โค้ดใหม่ให้ใช้
```python
from datetime import datetime, UTC
datetime.now(UTC)
```
ไม่ใช่ `datetime.utcnow()` (v1 ใช้แบบเก่าจึงมี warning 71 อัน)

---

## ภาคผนวก — ชุดเวอร์ชันที่ล็อกไว้

ทั้งหมดทดสอบร่วมกันบน **Python 3.12** — backend 33/33 · ai-engine 31/31

| package | version | ใช้ที่ |
|---|---|---|
| Flask | 3.0.3 | backend · ai-engine |
| Flask-Login | 0.6.3 | backend |
| Flask-Migrate | 4.0.7 | backend |
| Flask-SQLAlchemy | 3.1.1 | backend |
| Flask-WTF | 1.2.1 | backend |
| WTForms | 3.1.2 | backend |
| SQLAlchemy | 2.0.52 | database |
| alembic | 1.19.1 | database |
| opencv-python | 5.0.0.93 | ai-engine |
| numpy | 2.5.2 | ai-engine |
| scikit-image | 0.26.0 | ai-engine |
| scipy | 1.18.0 | ai-engine |
| matplotlib | 3.11.1 | ai-engine |
| Pillow | 12.3.0 | ทุก service |
| requests | 2.34.2 | ทุก service |
| pytest | 9.1.1 | ทุก service |

> `Pillow` · `requests` · `pytest` ตั้งเวอร์ชัน**เดียวกันทุก service** โดยตั้งใจ
> เพื่อให้ลงรวมใน venv เดียวได้โดยไม่ชนกัน

### เวลาจะอัปเกรดเวอร์ชัน

1. แก้ pin ในไฟล์ที่เกี่ยวข้อง
2. ลง env ใหม่จากศูนย์ (`rm -rf .venv` แล้วสร้างใหม่) — ไม่ใช่ `pip install -U` ทับ
3. รัน test ทุก service ให้ผ่านครบ
4. ถ้าแก้ package ที่ใช้ร่วมกัน (`Pillow` / `requests` / `pytest`) **ต้องแก้ทั้ง 3 ไฟล์พร้อมกัน**
5. อัปเดตตารางข้างบนนี้ + `environment.yml`
6. เปิด PR แยกสำหรับการอัปเกรด อย่าปนกับ feature
