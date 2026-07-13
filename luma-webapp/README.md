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