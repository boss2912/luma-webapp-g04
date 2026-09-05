# Worklog — คนที่ 2 · Data & Storage (`@boss2912`)

> แม่แบบ + กติกาการเขียนอยู่ที่ [`README.md`](README.md)
> **entry ใหม่อยู่บนสุดเสมอ** (ใหม่ → เก่า)

คิวงานของคุณ: [`../START_2_DATA.md`](../START_2_DATA.md)

---

## 2026-09-05 · #45 ปิดส่วนฐานข้อมูลของ Walking Skeleton

**branch**: `feat/skeleton-assets-table` · **สถานะ**: เสร็จ รอเปิด PR

**ทำอะไรไป**
- `flask db init` — ตั้งโครง Alembic ครั้งแรกของโปรเจกต์
  (ต้องลบ `.gitkeep` ออกก่อน เพราะ `db init` ปฏิเสธถ้าโฟลเดอร์ไม่ว่าง)
- `db migrate` + `db upgrade` — migration แรก `18566175f613` สร้างตาราง `assets`
  ตรวจไฟล์ก่อน upgrade แล้ว: ไม่มี drop/rename แฝง `downgrade()` ถอยกลับได้
- `services/database/tests/test_assets_table.py` — พิสูจน์ MUST 2 ข้อของ #45
- แก้คอมเมนต์ใน `asset.py` ที่ชี้ไป `schema/assets.sql` ซึ่งเป็นไฟล์ที่ไม่มีจริง
- แยก commit ของเอกสารทีม (AGENTS.md, START_*, worklog, CODEOWNERS) ออกจากงาน #45
  เพราะรวมกันแล้ว PR จะ ~1,500 บรรทัด เกินกติกา ~400 บรรทัดใน AGENTS.md
  และการแตะ `.github/` จะดึงทั้งทีมมารีวิว migration ที่เขาไม่เกี่ยว

**พิสูจน์แล้วว่าใช้ได้จริง**

| MUST ของ #45 | ผล |
|---|---|
| INSERT 3 แถวไม่ใส่ id -> ได้ id 1, 2, 3 | ผ่าน |
| ปิด connection แล้วเปิดใหม่ ข้อมูลยังอยู่ + เรียงใหม่->เก่าถูก | ผ่าน |
| NOT NULL กันได้จริงที่ระดับฐานข้อมูล | ผ่าน |

`python tools/check_all.py --with-tests` เขียวทั้ง 7 รายการ

**เรื่องที่ต้องรู้ (จดไว้กันลืม)**
- `default=utcnow` เป็น default ฝั่ง Python **ไม่ใช่** ฝั่งฐานข้อมูล จึงไม่ปรากฏใน
  migration เลย แปลว่า INSERT ด้วย raw SQL ที่ไม่ใส่ `created_at` จะ error ทันที
  เพราะคอลัมน์เป็น NOT NULL แต่ไม่มี server default — ต้อง INSERT ผ่าน ORM เท่านั้น
  หรือใส่ค่าเอง (เกี่ยวกับ ADR-008 ที่ให้ query เป็นไฟล์ .sql)
- `migrations/env.py` ที่ Flask-Migrate สร้างให้ ใช้ `get_engine()` ซึ่ง deprecated
  แล้ว จะพังเมื่ออัปเป็น Flask-SQLAlchemy 3.2 ตอนนี้ยังไม่กระทบเพราะ ADR-007
  ล็อกเวอร์ชันด้วย `==` — แต่โผล่เป็น warning ทุกครั้งที่รัน test

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. ยังไม่ push และยังไม่เปิด PR (ใส่ `Closes #45` ในคำอธิบาย PR)
2. งานถัดไปคือ #16 ตาราง `users` — คนที่ 1 รออยู่ (#49 สมัครสมาชิก, #50 login)
3. **ตาราง `jobs` ยังไม่ควรสร้างใน #16** — L4 หน้า 55 ระบุว่า queue เป็นงานคนที่ 3
   และข้อ 6 ของ `API_CONTRACT.md` ("ตาราง jobs ใครเขียน ใครอ่าน") ยังไม่ตกลง
   v1 เคยสร้างตาราง `Job` ทิ้งไว้โดยไม่มีโค้ดใช้มาแล้ว (COURSE_REQUIREMENTS ข้อ 11)

**รออะไรจากใคร**
- #17 ยังรอข้อ 5 ของ #32 (รูปแบบ auto-tag จากคนที่ 3) เหมือนเดิม

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
