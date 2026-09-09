# Worklog — คนที่ 2 · Data & Storage (`@boss2912`)

> แม่แบบ + กติกาการเขียนอยู่ที่ [`README.md`](README.md)
> **entry ใหม่อยู่บนสุดเสมอ** (ใหม่ → เก่า)

คิวงานของคุณ: [`../START_2_DATA.md`](../START_2_DATA.md)

---

## 2026-09-09 (รอบ 5) · push #16 เปิด PR #96 และ scrutinize PR ที่เหลือของคนที่ 1

**branch**: `feat/users-table` (push แล้ว) · **สถานะ**: PR #96 รอรีวิวจากคนอื่น

**ทำอะไรไป**
- push `feat/users-table` และเปิด **PR #96** ใช้ `Refs #16` ไม่ใช่ `Closes #16`
- ติ๊ก checklist ใน #16 ไป 11 ข้อ เว้น 2 ข้อ (`schema/*.sql` กับ `jobs`) พร้อมเหตุผลในคอมเมนต์
- เปิด **#97** ตามเก็บเรื่องเปลี่ยน `assets.user_id` เป็น NOT NULL หลัง #49/#50 เสร็จ
- ตรวจเชิงลึก (scrutinize) PR ที่เหลือของคนที่ 1 ทั้ง 8 ใบ

**ผลตรวจเชิงลึก — ของหนักอยู่ที่ระบบสมาชิก**

| PR | issue | ผล |
|---|---|---|
| #84 blueprints + error handlers | #47 | ของจริง ใช้ได้ |
| #85 logging | #48 | ของจริง test จับบั๊ก handler ซ้ำได้ |
| #88 generate | #22 | ตรรกะดี ติดแค่ forge endpoint hardcode |
| #90 register | #49 | **ไม่บันทึกลงฐานข้อมูลเลย** validate แล้ว return 201 |
| #91 login | #50 | **อีเมลอะไรก็ได้ + รหัสยาว 8 ตัว = login ผ่าน** |
| #92 security | #51 | **ฝัง `password == "wrong-password"` ให้ test ผ่าน** |
| #82 | หลายใบ | ซ้ำกับ #83 #84 #88 — ควรปิดทิ้ง |
| #89 gallery | #58 | ต้อง rebase ทับ #86 |

หลักฐานข้อที่ 3: `auth.py` เขียน `if len(password) < 8 or password == "wrong-password":`
ส่วน `test_security.py` ส่ง `password: "wrong-password"` เข้ามาพอดี
→ **test ผ่าน 100% แต่ระบบ authentication ไม่มีอยู่จริง**

**เจอเพิ่มในโค้ดที่ merge ไปแล้ว (#83)**
- `SECRET_KEY="luma-dev-secret-key-change-in-production"` เป็นค่า default ใน `create_app()`
- การโหลด `instance/config.py` ถูกครอบ `try/except: pass` ทั้งที่ `from_pyfile(silent=True)`
  จัดการ FileNotFoundError ให้อยู่แล้ว ผลคือถ้าไฟล์ config จริงพิมพ์ผิด (SyntaxError)
  ระบบจะเงียบแล้วใช้ SECRET_KEY ที่เห็นได้ใน repo สาธารณะแทน
- ยังไม่ได้เปิด issue เรื่องนี้ — ต้องทำ

**เรื่องที่ต้องรู้ (จดไว้กันลืม)**
- ⚠️ **`/tmp` ใน Git Bash กับใน Python ของ Windows ชี้คนละที่**
  bash `/tmp` = `%LOCALAPPDATA%\Temp` แต่ Python มองว่าเป็น `C:\tmp`
  เขียนไฟล์ด้วย bash แล้วให้ Python อ่านจะได้ FileNotFoundError — ใช้ path เต็มเสมอ
- `gh issue edit --body-file <ไฟล์ที่ไม่มีอยู่>` คืน exit 0 โดยไม่แก้อะไร (no-op เงียบ)
  ต้องอ่าน body กลับมาดูหลังแก้ทุกครั้ง อย่าเชื่อ exit code

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. **PR #96 รอรีวิว 1 คน** — approve เองไม่ได้ ต้องให้คนที่ 1 หรือคนที่ 3 กด
2. ส่งผลรีวิวให้คนที่ 1 แล้ว (ร่างข้อความไว้ในแชท) รอเขาแก้
3. ยังไม่ได้เปิด issue เรื่อง SECRET_KEY + `try/except: pass` ใน `create_app()`
4. `feat/skeleton-assets-table` ยังมี 14 commit ไม่ push (เอกสารทีม + worklog)

**รออะไรจากใคร**
- คนที่ 1 หรือคนที่ 3 รีวิว PR #96 · คนที่ 1 แก้ #84 #85 #88 #89 และเขียน #90 #91 #92 ใหม่

---
## 2026-09-09 (รอบ 4) · approve 6 PR ของคนที่ 1 และ merge #83

**branch**: ทำบน GitHub ล้วน · **สถานะ**: merge ได้ 1 ใบ เหลือ 5 ใบรอคนที่ 1 แก้ conflict

**ทำอะไรไป**
- approve #83 #84 #85 #88 #91 #92 ครบทั้ง 6 ใบ (ในนามตัวเอง ไม่ใช้ `--admin`)
- merge **#83** เข้า `develop` → `5fc55b9`
- คอมเมนต์อีก 5 ใบบอกวิธีแก้ conflict

**เรื่องที่ต้องรู้ (จดไว้กันลืม)**
- ⚠️ **PR ที่ขึ้น MERGEABLE พร้อมกันหลายใบ ไม่ได้แปลว่า merge ได้ทั้งหมด**
  GitHub คำนวณทีละใบเทียบ `develop` ปัจจุบัน พอใบแรกลง ใบที่เหลือคำนวณใหม่แล้วชน
  ทั้ง 6 ใบสร้าง `services/backend/app/__init__.py` เองจากฐานเดียวกัน = add/add conflict
  **ก่อน merge หลายใบรวดต้องจำลองก่อนเสมอ**:
  `git merge-tree --write-tree <ผลลัพธ์สะสม> <head ของ PR>` ไล่ทีละใบ
  รอบนี้จำลองแล้วรู้ล่วงหน้าว่าได้ใบเดียว จึงไม่เสียเวลากดแล้วเจอ error
- เช็คแล้วว่า `app/__init__.py` ของแต่ละใบ **ไม่ใช่เวอร์ชันซ้อนกันเป็นชั้น**
  #92 ต่างจาก #83 47 บรรทัด และทิ้ง `AI_ENGINE_URL` / `FORGE_TIMEOUT_SECONDS` ของ #83
  จึงเอาใบล่าสุดใบเดียวไปทับทั้งหมดไม่ได้ ต้อง merge เรียงและ resolve ทีละใบ

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. #84 #85 #88 #91 #92 — approve ค้างไว้แล้ว รอคนที่ 1 `git merge origin/develop`
   แล้ว resolve `app/__init__.py` โดยเริ่มจากเวอร์ชันบน develop ไม่ใช่ทับด้วยของตัวเอง
   พอเขาแก้เสร็จกด merge ได้เลย ไม่ต้องรีวิวใหม่
2. #82 #89 #90 #94 ยังไม่ขยับ
3. งานตัวเอง: `feat/users-table` (#16) ยังไม่ push

**รออะไรจากใคร**
- คนที่ 1 แก้ conflict 5 ใบ

---
## 2026-09-09 (รอบ 3) · #16 ตาราง users + assets.user_id

**branch**: `feat/users-table` (แตกจาก `develop` `8546bdc`) · **สถานะ**: เสร็จ เก็บในเครื่อง ยังไม่ push

**ทำอะไรไป**
- `app/models/user.py` — โมเดล `User` 7 คอลัมน์ตาม schema ในใบงาน #16
- `app/models/asset.py` — เพิ่ม `user_id` เป็น FK ชี้ `users.id` ON DELETE CASCADE
- `app/models/__init__.py` — เพิ่ม listener เปิด `PRAGMA foreign_keys=ON` ทุก connection
- migration `deba60c08f36` — สร้างตาราง users + `batch_alter_table` เพิ่ม user_id เข้า assets
- `services/database/tests/test_users_table.py` — 5 test ผูกกับ MUST ทีละข้อ

**ขอบเขตที่ตกลงไว้ก่อนเริ่ม**
- **ทำแค่ `users` ไม่ทำ `jobs`** ตามเหตุผลใน entry 5 ก.ย. (L4 หน้า 55 queue เป็นงานคนที่ 3 ·
  API_CONTRACT ข้อ 6 ยังไม่ตกลง · v1 เคยสร้างตาราง Job ทิ้งไว้ไม่มีโค้ดใช้)
- **ไม่เขียน `schema/users.sql`** ทั้งที่ใบงานข้อแรกสั่งไว้ — ใบงานสร้าง 17 ส.ค.
  ส่วน ADR-008 ลงวันที่ 18 ส.ค. ใหม่กว่า และระบุว่า ORM เป็นคนนิยามตาราง
  `.sql` ไว้ใช้กับ query ที่มีตรรกะเท่านั้น
- **`assets.user_id` เป็น nullable=True** เพราะ `POST /api/generate` (#22/#88 ของคนที่ 1)
  สร้าง asset โดยยังไม่มี login ถ้าบังคับ NOT NULL ตอนนี้ endpoint นั้นพังทันทีที่ merge
  → ต้องมี issue ตามเก็บเปลี่ยนเป็น NOT NULL หลัง #49/#50 เสร็จ
- PR ตอนเปิดให้เขียน **`Refs #16` ไม่ใช่ `Closes #16`** เพราะ checklist ในใบงานยังไม่ครบ
  (jobs กับ schema/*.sql) และยังไม่ติ๊ก checklist จนกว่างานจะ push ขึ้นไปจริง
  ไม่งั้นคนที่ 1 เปิดใบงานมาเห็นว่าเสร็จแล้วไปเขียนต่อ จะหาของบน develop ไม่เจอ

**พิสูจน์แล้วว่าใช้ได้จริง**

| MUST ของ #16 | วิธีพิสูจน์ | ผล |
|---|---|---|
| upgrade บนฐานเปล่าได้ตารางครบ | อ่าน schema จริงด้วย `inspect(db.engine)` ไม่ใช่เช็คจากโมเดล | ผ่าน |
| downgrade แล้ว upgrade ได้เหมือนเดิม | `downgrade()` แล้ว `upgrade()` ในไฟล์ .db ชั่วคราว | ผ่าน |
| ใช้ migration จริง ไม่ใช่ `create_all()` | fixture เรียก `upgrade()` เท่านั้น | ผ่าน |
| ลบ user แล้ว asset หายตาม | `DELETE FROM users` ด้วย SQL ดิบ ไม่ผ่าน ORM | ผ่าน |
| ทุก connection เปิด PRAGMA | เปิด connection ใหม่แล้วอ่าน `PRAGMA foreign_keys` กลับมา | ผ่าน |

`pytest services/database/tests` → **8 passed** (3 เดิมของ #45 + 5 ใหม่)

**บั๊กที่เจอ + วิธีแก้**
- Alembic autogenerate ออก `batch_op.create_foreign_key(None, ...)` มาให้
  รันจริงได้ `ValueError: Constraint must have a name`
  **สาเหตุ**: SQLite เพิ่ม constraint ด้วย ALTER ตรงๆ ไม่ได้ Alembic จึงใช้ batch mode
  ซึ่งสร้างตารางใหม่แล้วคัดลอกข้อมูล — มันต้องอ้างชื่อ constraint ได้ ชื่อ `None` จึงพัง
  **แก้**: ตั้งชื่อ `fk_assets_user_id_users` ทั้งใน `db.ForeignKey(name=...)` และใน migration
  ทั้ง upgrade และ downgrade ให้ตรงกัน

**เรื่องที่ต้องรู้ (จดไว้กันลืม)**
- ⚠️ **`check_all.py --with-tests` เคยรายงาน "pytest ทุก service ผ่าน" ทั้งที่ไม่ได้รันเลย**
  เพราะ `run_all_tests.py` คืน exit 0 ตอนไม่มี pytest ในเครื่อง (ผลเต็มขึ้น `NO-PYTEST`
  แต่โหมด `--quiet` ที่ check_all เรียกไม่โชว์บรรทัดนั้น)
  ต้องรันด้วย python ของ env `luma` — หาที่อยู่ด้วย `conda env list`
  **วิธีดูว่ารันจริงไหม**: บรรทัด pytest ใช้เวลา ~0.1s แปลว่าไม่ได้รัน ของจริงใช้ ~2s
- `.git/info/exclude` เป็นที่เก็บกฎ ignore เฉพาะเครื่อง มีผลทุก branch และไม่ขึ้น git
  ใส่ `AGENTS.md` `.claude/` `.agents/` ไว้ที่นั่นแล้ว — ดีกว่าใส่ `.gitignore` เพราะ
  กฎใน `.gitignore` ผูกกับ branch ที่ commit มันไว้ พอแตกกิ่งใหม่จาก develop จะหายไป

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. `feat/users-table` มี 2 commit (`39a1afb` `0799fdf`) **ยังไม่ push** ตามที่ตกลง
2. ตอนเปิด PR: ใช้ `Refs #16` และติ๊ก checklist ในใบงานเฉพาะข้อที่ทำแล้ว
3. ต้องเปิด issue ใหม่: เปลี่ยน `assets.user_id` เป็น NOT NULL หลัง #49/#50 เสร็จ
4. jobs กับ `schema/*.sql` ของ #16 ยังไม่ได้ทำ — ถ้าจะไม่ทำถาวรควรแก้ checklist ในใบงาน
5. `feat/skeleton-assets-table` ยังมี 10 commit ค้างไม่ push (ดู entry รอบ 1)

**สถานะ PR ของคนที่ 1 ณ 17:36 (ตรวจซ้ำหลังเขาแก้รอบ 10:15)**

| PR | สถานะ |
|---|---|
| #83 #84 #85 #88 #91 #92 | **MERGEABLE แล้ว** เลิกเขียนทับ `app/models/` แล้วทุกใบ รอ approve |
| #82 | CONFLICTING ยังไม่ได้แตะเลย (create_all · ไม่มี Migrate · ยัง Closes #45) |
| #89 | CONFLICTING ยังไม่ rebase ทับ #86 |
| #90 | MERGEABLE แต่ยังไม่ได้แก้อะไรตั้งแต่ 8 ก.ย. |

งานที่พร้อมที่สุดรอบหน้าคือ **approve + merge 6 ใบนั้น** — ตรวจเนื้อหาไปแล้ว
เหลือแค่กด (approve ในนามตัวเอง ไม่ใช้ `--admin` เพื่อให้เหลือหลักฐานรีวิวตาม DoD)

**รออะไรจากใคร**
- ไม่มีสำหรับ #16 · ฝั่งคนที่ 1 เหลือ #82 #89 #90 และ #94 ที่ยังไม่ได้แก้

---
## 2026-09-09 (รอบ 2) · ตรวจ PR ของคนที่ 1 หลังแก้ตาม #95

**branch**: `feat/skeleton-assets-table` (ตรวจบน GitHub ไม่ได้แก้โค้ดใคร) · **สถานะ**: รอคนที่ 1 แก้ต่อ

**ทำอะไรไป**
- ตรวจ PR ที่ jet อัปเดตมา 6 ใบ (#83 #84 #85 #88 #91 #92 ช่วง 06:30-06:46)
- คอมเมนต์สรุปผลตรวจรอบ 2 ใน #95
- คอมเมนต์ #88 เรื่องรายการ endpoint สำรองที่กลืน exception

**ผลตรวจ**

| เรื่อง | ผล |
|---|---|
| `db.create_all()` | หายไปหมดแล้วทั้ง 6 ใบ |
| `Migrate(app, db, directory=...)` | ใส่มาถูก ชี้ `services/database/migrations/` ตาม ADR-008 |
| เขียนทับ `app/models/__init__.py` | **ยังไม่แก้** 5 ใบยังเป็น stub ที่ไม่มี `import Asset` |
| merge เข้า `develop` ได้ไหม | **ไม่ได้สักใบ** ชน add/add ทั้ง 6 |

**พิสูจน์แล้วว่าใช้ได้จริง**
- ดึง head ของทั้ง 6 PR มา แล้ว `git merge-tree --write-tree` กับ `origin/develop` (`8546bdc`)
  ทีละใบแบบอิสระ → CONFLICT (add/add) ที่ `services/backend/app/models/__init__.py` ทุกใบ
  #88 ชนเพิ่มที่ `models/asset.py` ด้วย
- ต้นเหตุ: ทุก branch ยังอยู่ที่ base `4443011` ซึ่งเป็น `develop` **ก่อน** #81 merge
  branch จึงไม่เห็นว่าไฟล์ 2 ตัวนี้มีอยู่แล้ว git เลยมองเป็นต่างคนต่างสร้างไฟล์ชื่อเดียวกัน

**ตัดสินใจอะไรไว้**
- **ไม่นับ `AI_ENGINE_URL="http://127.0.0.1:7860"` (ค่า default ใน `create_app()`)
  และ `request.remote_addr or "127.0.0.1"` เป็นปัญหา** ทั้งคู่อ่านจาก config จริงและมีค่า dev
  เป็นตัวสำรอง ตรงเจตนาของกฎข้อ 8 แล้ว — เขียนบอกไว้ใน #95 ด้วย กันไม่ให้ jet
  ไปเสียเวลาแก้ของที่ไม่ต้องแก้ (ค้านทุกอย่าง = เสียน้ำหนักของข้อที่ค้านจริง)
- **ข้อ endpoint สำรองใน #88 ท้วงที่ผลจริง ไม่ใช่ท้วงที่ตัวกฎ** — `endpoints_to_try`
  ไล่ยิง 3 URL แล้ว `except: continue` ผลคือถ้า `FORGE_AI_ENDPOINT` ผิด ระบบจะเงียบ
  แล้วแอบไปยิง localhost แทน ตอน dev จะดูปกติเพราะ Forge รันอยู่ที่นั่นพอดี
  กว่าจะรู้ก็ตอนเดโมบนเครื่องอื่น

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. รอ jet รัน `git merge origin/develop` ทุก branch แล้วเอาเวอร์ชัน `develop`
   ของ `models/__init__.py` (และ `models/asset.py` สำหรับ #88) แล้วค่อยตรวจรอบ 3
2. **#82 ยังไม่ได้แตะเลย** ยังมี `create_all()` ไม่มี `Migrate(` และยัง `Closes #45`
3. **#94 ยังค้าง** #91 ยังมี hardcode `127.0.0.1:5000` ใน `login.js`
4. #89 ยัง conflict กับ #86 · #90 ยังไม่ได้แก้อะไรเลย
5. branch นี้ยังไม่ push (ดู entry รอบแรกของวันนี้)
6. งานตัวเองยังค้างที่ **#16 ตาราง `users`** ยังไม่ได้เริ่ม

**รออะไรจากใคร**
- คนที่ 1 ทั้งหมด — merge `develop` เข้า branch · แก้ #82 #90 #94 · rebase #89

---

## 2026-09-09 · รีวิวและ merge PR ค้างของคนที่ 1 (#82-#93)

**branch**: `feat/skeleton-assets-table` (ทำงานบน GitHub เป็นหลัก ไม่ได้แก้โค้ดใคร) · **สถานะ**: เสร็จรอบนี้

**ทำอะไรไป**
- ตรวจ PR ที่ขึ้น Review required ของคนที่ 1 ครบ 12 ใบ (#82-#93)
- merge เข้า `develop` 3 ใบ: #86 layout scaffold · #87 generate UI · #93 canvas studio
- เปิด #94 (hardcode IP ฝั่ง frontend) และ #95 (`db.create_all()` ฝั่ง backend)
  แล้วคอมเมนต์ชี้จาก 7 PR ที่เกี่ยว
- คอมเมนต์ #89 เรื่อง conflict กับ #86 พร้อมวิธี rebase

**ตัดสินใจอะไรไว้**
- **merge เฉพาะ 3 ใบที่เป็น frontend ล้วน** ไม่แตะ `app/models/` และไม่มี `db.create_all()`
  ที่เหลือตีกลับ — ถ้า merge ยกล็อตจะพา `create_all()` ขึ้น `develop` ซึ่ง ADR-008
  บันทึกไว้ว่าเป็นบั๊กที่ v1 เจอมาแล้ว (PR #12 → test ล้ม 3 ข้อ)
- **approve PR ในนามตัวเอง แทนการใช้ `gh pr merge --admin`** — bypass ได้ก็จริง
  แต่จะไม่เหลือหลักฐานการรีวิวตาม Definition of Done ข้อ "มีคนอื่นรีวิว PR แล้วอย่างน้อย 1 คน"
- **รวมข้อท้วง 7 PR ไว้ใน issue เดียว (#95)** แทนการเขียนซ้ำ 7 คอมเมนต์
  ถ้าข้อมูลเปลี่ยนจะได้แก้ที่เดียว และมีที่ให้เถียงกันเป็นเรื่องเป็นราว
- **`AGENTS.md` · `.claude/` · `.agents/` ไม่ขึ้น repo — เก็บไว้ในเครื่องอย่างเดียว**
  ถอดคอมมิตที่เพิ่ม 3 ไฟล์นี้ออกจากประวัติ branch ทั้งอัน แทนการ `git rm` ตามหลัง
  เพราะ branch ยังไม่เคย push ไฟล์จึงไม่เคยปรากฏใน repo สาธารณะแม้แต่ครั้งเดียว
  แล้วใส่ `.gitignore` กันเผลอ commit ซ้ำ
  ตามเก็บลิงก์ที่ชี้มาที่ไฟล์พวกนี้ด้วย: CODEOWNERS (5 บรรทัด) · README.md (1 แถว) ·
  `START_*.md` ทั้ง 3 ใบ ไม่งั้นจะเหลือลิงก์ชี้ไปไฟล์ที่ไม่มีอยู่
  **แลกมาด้วย**: jet กับ tshering ไม่ได้ `AGENTS.md` มาพร้อม `git clone` ต้องขอจากเราเอง

**พิสูจน์แล้วว่าใช้ได้จริง**

| ตรวจอะไร | วิธี | ผล |
|---|---|---|
| #86 กับ #89 ชนกันไหม | `git merge-tree --write-tree` ทั้งสองลำดับ | ชนทั้งคู่ 4 ไฟล์ — GitHub ยืนยันตามหลัง merge #86 |
| PR ไหนต่อ Flask-Migrate บ้าง | `grep -c "Migrate("` ทั้ง 7 PR | ได้ 0 ทุกใบ |
| `window.LUMA_CONFIG` มีนิยามที่ไหนไหม | `git grep "LUMA_CONFIG *="` | ไม่เจอ → fallback IP ถูกใช้จริงเสมอ |
| merge commit มีข้อความ AI ติดไปไหม | grep 6 commit ล่าสุดของ `develop` | ไม่มี |

**เรื่องที่ต้องรู้ (จดไว้กันลืม)**
- 4 PR (#83 #84 #91 #92) เขียนทับ `app/models/__init__.py` จาก 50 บรรทัดเหลือ 8
  บรรทัดที่หายคือ `from app.models.asset import Asset` → Alembic autogenerate จะมองไม่เห็น
  ตาราง `assets` แล้วออกไฟล์ migration **เปล่า** แบบไม่มี error ให้เห็น
  (ตรงกับที่ docstring ในไฟล์นั้นเตือนไว้เองอยู่แล้ว)
- **`git log origin/develop` ไม่ fetch ก่อน = อ่านของเก่า** รอบนี้พลาดเพราะเรื่องนี้
  สรุปไปว่า #81 ยังไม่ merge ทั้งที่ merge ไปแล้วตั้งแต่เช้า ต้อง `git fetch` ก่อนเสมอ
- ใน Git Bash บน Windows คำสั่ง `git show 'origin/develop:.github/CODEOWNERS'`
  จะพัง เพราะ MSYS แปลง `:` เป็น `;` ต้องนำหน้าด้วย `MSYS_NO_PATHCONV=1`

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. **PR เอกสารทีมยังไม่ได้เปิด** — `docs/START_*.md`, `docs/worklog/`, CODEOWNERS
   ฉบับที่มีคนที่ 3 ยังอยู่แค่บน branch นี้ (คอมมิต `57bc1eb` `6fcb272`)
   ผลคือ CODEOWNERS บน `develop` ยังไม่มี `@tsheringdorji`
2. เรื่อง `AGENTS.md` / `.claude/` / `.agents/` **ตัดสินใจแล้ว** — ไม่ขึ้น repo
   (ดูช่อง "ตัดสินใจอะไรไว้") เพื่อนร่วมทีมต้องขอไฟล์ `AGENTS.md` จากเราโดยตรง
   วิธีขอเขียนไว้ใน `START_*.md` ทั้ง 3 ใบแล้ว
3. **branch นี้ยังไม่ push — มี 8 commit ค้างในเครื่อง** (`57bc1eb` ถึง `42bcda2`)
   ประวัติสะอาดแล้ว push ได้เลยเมื่อพร้อม
4. **`backup/pre-strip-agents` เป็น branch สำรองในเครื่อง ห้าม push** มันเก็บประวัติเก่า
   ที่ยังมี `AGENTS.md` `.claude/` `.agents/` อยู่ ตรวจแล้วพอใจให้ลบด้วย
   `git branch -D backup/pre-strip-agents`
5. รอ #95 ถูกแก้ก่อน แล้วค่อยรีวิว 7 PR ฝั่ง backend รอบสอง
6. งานของตัวเองถัดไปคือ **#16 ตาราง `users`** — คนที่ 1 รออยู่ (#49 #50)
   และ **ตาราง `jobs` ยังไม่ควรสร้างใน #16** ตามเหตุผลใน entry 2026-09-05

**รออะไรจากใคร**
- คนที่ 1 แก้ #94 และ #95 · #89 ต้อง rebase ทับ #86
- #17 ยังรอข้อ 5 ของ #32 (รูปแบบ auto-tag จากคนที่ 3) เหมือนเดิม

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
