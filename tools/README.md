# tools/ — สคริปต์ช่วยงาน

สคริปต์ที่ใช้พัฒนา/ตรวจงาน **ไม่ใช่ส่วนของระบบที่ deploy**
รันจาก root ของ repo เสมอ

---

## มีอยู่แล้ว

### `smoke_test_ai_deps.py`

ตรวจว่า dependency ของ `ai-engine` ติดตั้งถูกและ**ใช้งานร่วมกันได้จริง**
ไม่ใช่แค่ import ผ่าน แต่เรียก 31 operation ที่ pipeline 5 ส่วนต้องใช้จริงกับภาพทดสอบ

```bash
python tools/smoke_test_ai_deps.py
```

ครอบ: `imread` · `cvtColor` HSV · `filter2D` · `sepFilter2D` · `medianBlur` ·
`equalizeHist` · LUT gamma · `dft`/`idft` · `morphologyEx` · Otsu · `findContours` ·
`Canny` · alpha merge · `contourArea` · skew/kurtosis · PSNR · SSIM · IoU ·
matplotlib headless savefig · PIL interop

**ใช้ตอน**: ตั้งเครื่องใหม่ · หลังลง requirements ครั้งแรก · หลังอัปเกรดเวอร์ชัน

> ยืนยันแล้วว่าผ่าน 31/31 บน Python 3.12 กับชุดเวอร์ชันที่ล็อกไว้ใน
> `services/ai-engine/requirements.txt`

### `check_requirements_ascii.py`

ตรวจว่าไฟล์ `requirements*.txt` ทุกไฟล์เป็น **ASCII ล้วน**

```bash
python tools/check_requirements_ascii.py
```

**ทำไมต้องตรวจ**: pip อ่านไฟล์ requirements ด้วย codec ของ locale เครื่อง ไม่ใช่ UTF-8
บน Windows ภาษาไทย locale คือ `cp874` ถ้าไฟล์เป็น UTF-8 ที่มีตัวอักษรไทย
`pip install -r` จะพังด้วย `UnicodeDecodeError`

นี่เป็นปัญหาจริงที่เจอใน v1 — ดู [`../archive/ARCHITECTURE_v1.md`](../archive/ARCHITECTURE_v1.md) ปัญหา B
คำอธิบายภาษาไทยให้ไปอยู่ใน [`../INSTALL.md`](../INSTALL.md) แทน

ใช้เป็น pre-commit hook ได้:

```bash
python tools/check_requirements_ascii.py || exit 1
```

---

## ยังต้องทำ

- [ ] **mock Forge AI server** — ทดสอบ backend โดยไม่ต้องเปิด Stable Diffusion จริง
      ตอบ PNG 1×1 base64 กลับมา (ดูเทคนิคใน `../archive/ARCHITECTURE_v1.md` ข้อ 11)
- [ ] **สคริปต์ตรวจว่าไม่มี secret / ไฟล์ `.db` หลุดขึ้น git**
      เช็คก่อน commit ว่าไม่มี `config.py`, `.env`, `*.db` ใน staged files
- [ ] **สคริปต์รวม test ทุก service** — รัน pytest ทั้ง 3 service แล้วสรุปผลรวม
- [ ] **สคริปต์ตรวจลิงก์ใน .md** ว่าชี้ไปไฟล์ที่มีจริง (มีการตรวจแล้วตอนวางโครง 26/26 ผ่าน
      แต่ยังไม่ได้ทำเป็นสคริปต์ถาวร)
