# study/ — โฟลเดอร์ซ้อมมือ SQLite

> ⚠️ **ไม่ใช่ deliverable** ไฟล์ในนี้ไม่มีอะไรที่ระบบจริงเรียกใช้
> เป็นที่ลองคำสั่งจากสไลด์ให้เข้าใจก่อนเอาไปใช้จริงใน `../schema/` และ `../queries/`

## ทำไมแยกโฟลเดอร์

`../tests/` เก็บ **test จริงที่ `pytest` รัน** — ถ้าเอาสคริปต์ซ้อมไปปนกันไว้
เวลาอ่านจะแยกไม่ออกว่าอันไหนคือเงื่อนไขความสำเร็จของ issue อันไหนคือของเล่น

## ไฟล์ในนี้

| ไฟล์ | ซ้อมอะไร | อ้างอิง |
|---|---|---|
| `00-basic-sqlite.py` | `connect` · `execute` · `commit` · `close` | Lecture 7 หน้า 99–108 |

## รันยังไง

```bash
conda activate luma
python services/database/study/00-basic-sqlite.py
```

ไฟล์ `.db` ที่สคริปต์สร้างจะอยู่ **ข้างตัวสคริปต์เสมอ** ไม่ว่าจะรันจากโฟลเดอร์ไหน
เพราะใช้ `os.path.dirname(os.path.abspath(__file__))` แทนการเขียนชื่อไฟล์เฉยๆ

> ถ้าเขียน `sqlite3.connect("backup.db")` ตรงๆ ไฟล์จะไปโผล่ตรงโฟลเดอร์ที่รันคำสั่ง
> ซึ่งเปลี่ยนไปเรื่อยๆ แล้วจะงงว่าข้อมูลที่เพิ่งใส่หายไปไหน

## ⛔ ไฟล์ `.db` ห้าม commit

`.gitignore` ครอบ `*.db` ทุกที่อยู่แล้ว **อย่าปลด**

v1 เคยมี `instance/luma.db` ค้างใน git (ถูก commit ก่อนที่กฎ ignore จะถูกเพิ่ม)
พอ PR เพิ่มคอลัมน์ใหม่ → **test ล้ม 3 ข้อ** เพราะ schema ในไฟล์เก่าไม่ตรงกับโค้ด
รายละเอียดอยู่ใน [`../README.md`](../README.md)

## เปิดไฟล์ `.db` ดูยังไง

[DB Browser for SQLite](https://sqlitebrowser.org) — อาจารย์แนะนำไว้ใน Lecture 7 หน้า 102
เปิดไฟล์ `.db` แล้วเห็นตารางกับข้อมูลเป็น GUI ไม่ต้องพิมพ์ `SELECT` ทุกครั้ง

## ซ้อมต่อได้ที่ไหน

- cheat sheet 5 ใบใน `Resource_SQL_ Database/` — ใบที่ 5 คือ window function
  ซึ่งเป็นตัวที่ Asset Hub ต้องใช้จริง (ดูตาราง query ใน [`../README.md`](../README.md))
- เกมฝึก SQL ที่อาจารย์แนะนำ (Lecture 7 หน้า 109–110):
  [sqlsidequest.com](https://www.sqlsidequest.com) · [sqlnoir.com](https://www.sqlnoir.com)

## ซ้อมเสร็จแล้วไปไหนต่อ

ของจริงอยู่ที่ [#45 Walking Skeleton](https://github.com/boss2912/luma-webapp-g04/issues/45)
— ตาราง `assets` 4 คอลัมน์ (`id`, `prompt`, `file_path`, `created_at`) + migration แรก

และอย่าลืม [ADR-008](../../../docs/DECISIONS.md) — ของจริง SQL ดิบเขียนใน `../queries/*.sql`
และต้องใช้ named parameter `:name` เสมอ **ห้ามต่อสตริง**
