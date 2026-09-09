# study/ — โฟลเดอร์ซ้อมมือ SQLite

> ⚠️ **ไม่ใช่ deliverable** ไฟล์ในนี้ไม่มีอะไรที่ระบบจริงเรียกใช้
> เป็นที่ลองคำสั่งจากสไลด์ให้เข้าใจก่อนเอาไปใช้จริงใน `../schema/` และ `../queries/`

## ทำไมแยกโฟลเดอร์

`../tests/` เก็บ **test จริงที่ `pytest` รัน** — ถ้าเอาสคริปต์ซ้อมไปปนกันไว้
เวลาอ่านจะแยกไม่ออกว่าอันไหนคือเงื่อนไขความสำเร็จของ issue อันไหนคือของเล่น

## ไฟล์ในนี้

รันตามลำดับเลขหน้าไฟล์ แต่ละไฟล์ต่อยอดจากไฟล์ก่อนหน้า

| ไฟล์ | ซ้อมอะไร | อ้างอิง |
|---|---|---|
| `00-basic-sqlite.py` | `connect` · `execute` · `commit` · `close` | Lecture 7 หน้า 99–108 |
| `01-create-table.py` | หัวตาราง — `PRIMARY KEY AUTOINCREMENT` · `NOT NULL` · `UNIQUE` · `DEFAULT` | สไลด์ Create |
| `02-insert-mock.py` | `INSERT` · named parameter `:name` · `executemany` · `INSERT OR IGNORE` | สไลด์ Create |
| `03-read.py` | `fetchone` → `fetchall` · `WHERE` · `ORDER BY` · `LIMIT` · `GROUP BY` · `HAVING` | สไลด์ Read (2 รูป) |
| `04-update-delete.py` | `UPDATE … WHERE` · `DELETE … WHERE` · `rowcount` | สไลด์ Update, Delete |
| `05-assets-luma.py` | แพตเทิร์นเดิมบนตาราง `assets` ของจริง | [#45](https://github.com/boss2912/luma-webapp-g04/issues/45) |

`00-` สร้าง `backup.db` แยกของตัวเอง ส่วน `01-`–`05-` ใช้ `study.db` ไฟล์เดียวกันหมด
(`05-` เพิ่มตาราง `assets` เข้าไปในไฟล์เดิม → เปิด DB Browser ครั้งเดียวเห็นทั้ง `users` และ `assets`)

### หัวตารางที่ซ้อม

```
users    id · name · email · points · accuracy      ← ตามสไลด์ ไฟล์ 01–04
assets   id · prompt · file_path · created_at       ← ของจริง #45 ไฟล์ 05
```

## รันยังไง

```bash
conda activate luma
python services/database/study/01-create-table.py
python services/database/study/02-insert-mock.py
python services/database/study/03-read.py
python services/database/study/04-update-delete.py
python services/database/study/05-assets-luma.py
```

**ต้องเรียงลำดับ** — `02-` ใส่ข้อมูลลงตารางที่ `01-` สร้าง ถ้าข้าม `01-` จะเจอ
`no such table: users`

**รันซ้ำได้** — `02-` ใช้ `INSERT OR IGNORE` คู่กับ `email` ที่เป็น `UNIQUE`
รันกี่รอบข้อมูลก็เท่าเดิม (ยกเว้น `05-` ที่ตั้งใจให้ asset เพิ่มทุกรอบ — เหตุผลอยู่ท้ายไฟล์)

**อยากเริ่มใหม่หมด** — ลบ `services/database/study/study.db` ทิ้งแล้วรัน `01-` ใหม่

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

`05-assets-luma.py` คือสะพานไปหางานนั้น — หัวตารางชุดเดียวกันเป๊ะ ต่างกันตรงที่
**ของจริง `CREATE TABLE` ต้องไปอยู่ใน `../schema/*.sql` แล้วเปลี่ยนผ่าน migration**
ไม่ใช่ฝังในสคริปต์ Python แบบที่ซ้อม ท้ายไฟล์ `05-` เขียนความต่างไว้ครบ 3 ข้อ

และอย่าลืม [ADR-008](../../../docs/DECISIONS.md) — ของจริง SQL ดิบเขียนใน `../queries/*.sql`
และต้องใช้ named parameter `:name` เสมอ **ห้ามต่อสตริง**
