# Worklog — คนที่ 2 · Data & Storage (`@boss2912`)

> แม่แบบ + กติกาการเขียนอยู่ที่ [`README.md`](README.md)
> **entry ใหม่อยู่บนสุดเสมอ** (ใหม่ → เก่า)

คิวงานของคุณ: [`../START_2_DATA.md`](../START_2_DATA.md)

---

## 2026-08-29 · #45 ตาราง `assets` สำหรับ Walking Skeleton

**branch**: `feat/skeleton-assets-table` · **สถานะ**: กำลังทำ

**ทำอะไรไป**
- `services/backend/app/models/__init__.py` — สร้าง `db = SQLAlchemy()` ไว้ในโฟลเดอร์ `models/`
- `services/backend/app/models/asset.py` — โมเดล `Asset` 4 คอลัมน์ (`id`, `prompt`, `file_path`, `created_at`) + `to_dict()` ตาม `docs/API_CONTRACT.md`
- `services/database/migrate_app.py` — app ตัวเล็กสำหรับรัน `flask db ...` โดยเฉพาะ

**ตัดสินใจอะไรไว้**
- วาง `db` ไว้ที่ `app/models/__init__.py` **ไม่ใช่** `app/__init__.py` ตามที่ตำรา Flask ส่วนใหญ่ทำ
  เพราะ `app/__init__.py` เป็นของคนที่ 1 คนเดียว ถ้าวางที่นั่นจะเกิด circular import
  และคนที่ 2 จะแก้ตารางไม่ได้เลยจนกว่าคนที่ 1 จะเขียน `create_app()` เสร็จ = บล็อกกันโดยไม่จำเป็น
- สร้าง `migrate_app.py` แยก แทนที่จะรอ `create_app()` ของคนที่ 1 — #45 ระบุเองว่า *"ไม่ต้องรอกัน"*
- ใช้ ORM นิยามตาราง ไม่ใช่เขียน `.sql` ตรงๆ ตาม ADR-008

**เรื่องที่ต้องรู้ (จดไว้กันลืม)**
- SQLite ไม่มีชนิด `DATETIME` จริง — SQLAlchemy **ตัด timezone offset ทิ้งเงียบๆ** ตอนเขียน
  ค่าในฐานข้อมูลเป็น UTC แต่ Python อ่านกลับมาได้ `tzinfo = None`
  → ห้ามเอาไปเทียบกับ `datetime.now()` ตรงๆ
- `default=utcnow` ไม่ใช่ `default=utcnow()` — ใส่วงเล็บแล้วทุกแถวจะได้เวลาเดียวกันหมด

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. ไฟล์ทั้ง 3 **ยังไม่ commit**
2. `services/database/migrations/` ยังว่าง (มีแค่ `.gitkeep`) → ต้องรัน `flask --app services/database/migrate_app db init` ก่อน แล้วค่อย `db migrate` + `db upgrade`
3. `asset.py` อ้างถึง `services/database/schema/assets.sql` ในคอมเมนต์ แต่ไฟล์นั้นยังไม่มี — ต้องเขียนเพิ่มหรือลบคอมเมนต์
4. ยังไม่ได้พิสูจน์ MUST 2 ข้อของ #45: INSERT 3 แถวได้ `id` 1/2/3 เอง · `ORDER BY created_at DESC` เรียงถูก

**รออะไรจากใคร**
- ไม่มีสำหรับ #45 · แต่ **#17 ต้องรอข้อ 5 ของ #32** (รูปแบบ auto-tag จากคนที่ 3) ก่อนสร้างตาราง `tags`
