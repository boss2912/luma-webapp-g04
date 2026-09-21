# Worklog — คนที่ 2 · Data & Storage (`@boss2912`)

> แม่แบบ + กติกาการเขียนอยู่ที่ [`README.md`](README.md)
> **entry ใหม่อยู่บนสุดเสมอ** (ใหม่ → เก่า)

คิวงานของคุณ: [`../START_2_DATA.md`](../START_2_DATA.md)

---

## 2026-09-21 · ตรวจ PR ทั้ง 11 ตัว + เปิด PR #112 เอาไฟล์ "เริ่มตรงนี้" ขึ้น develop

**branch**: `docs/start-here-per-person` (ใหม่ ตัดจาก develop) · **สถานะ**: PR #112 เปิดแล้ว รอรีวิว

**ตรวจ PR ทั้งหมดที่เปิดค้าง 11 ตัว (ไล่ diff จริง ไม่ได้ดูแค่สถานะ)**
- #110 ของเราเอง merge ได้ แต่ 0 review รอคนอื่นกด · #99 ยังค้างที่ฝั่งเราตัดสิน head ไม่ขยับตั้งแต่ 19 ก.ย.
- #80 `CONFLICTING` + 3,386 บรรทัด นิ่ง 12 วัน งานถูกซอยไป #83-#93 ที่ merge แล้ว → ควรปิดทิ้ง
- draft ของคนที่ 3 ทั้ง 8 ตัว (#102-109) ยังเป็น draft ทุกตัว 0 review 0 comment ไม่มีใครรีวิวได้

**ผลตรวจเนื้อ draft 8 ตัว — ที่ผ่านจริง**
- ไม่มี `import flask` ใน `pipeline/` เลยแม้แต่ไฟล์เดียว (AGENTS ข้อ 8.2)
- docstring อ้างเลขหน้าสไลด์จริง เช่น `Lecture 3, pp. 55-56`, `Lecture 4, p. 27` (ข้อ 8.3)
- test เป็นแบบรู้คำตอบล่วงหน้าตามข้อ 7: `gamma(img, 1.0)` ได้ภาพเดิม · `filter_separable` เท่ากับ 2D ·
  วงกลมกลมกว่าสี่เหลี่ยม · `skimage`/`Pillow`/`scipy` ที่ test ใช้ มีใน requirements.txt อยู่แล้ว ไม่ต้องแก้

**ผลตรวจ draft 8 ตัว — 4 ข้อที่ต้องแก้ก่อน merge**
1. `scope` commit ผิดทุกตัว: #103/#104 ใช้ `ip` (ไม่มีในรายการที่อนุญาต) · #105-109 ใช้ `ai` ทั้งที่เป็นงาน
   pipeline ล้วน → `git log --grep pipeline` จะได้ศูนย์ ทั้งที่ pipeline คือเกณฑ์ 40%
2. `samples/output/` ยังว่างทั้ง 8 PR (ใส่แค่ `samples/input/`) → ข้อ 8.4 ไม่ผ่าน
3. #103 รับ path ตรงๆ (`load(path)`, `read_exif(path)`) ขัดข้อ 8.1 — แต่ 01_acquisition คืองานอ่านไฟล์
   โดยธรรมชาติ ต้องตัดสินว่าจะยกเว้นแล้วเขียนลง DECISIONS.md หรือแยกชั้น io ออก
4. #102 ตัด branch จาก `main` ไม่ใช่ `develop` → พา merge commit ฝั่ง release 10 ตัวที่ยังไม่อยู่ใน develop
   เข้ามาด้วย (`f49f5ee`, `e951470`, `3ef769e` เช็คแล้ว `--is-ancestor` = NO ทั้งหมด) diff จริง +260/-0 ปลอดภัย
- และที่สำคัญกว่า 4 ข้อข้างบน: merge ทั้ง 8 ตัวแล้ว **#101 ยังไม่ถูกแก้** เพราะ #102 เปิดแค่
  `POST /forge/txt2img` ไม่มี `/pipeline/*` เลย โค้ด palette ใน #108 จึงไม่มีทางถูกเรียกจากเว็บ

**เปิด PR #112**
- `docs/START_1_WEB.md`, `START_2_DATA.md`, `START_3_AI_IP.md` ไม่เคยอยู่บน develop หรือ main เลย
  อยู่แค่บน `feat/skeleton-assets-table` → คนที่ 1 กับ 3 ที่ clone develop ไม่เคยเห็นคิวงานตัวเอง
- ตัดหัวข้อ "ทำงานกับ AI" ออกจากทั้ง 3 ไฟล์ (25/24/27 บรรทัด) และไม่เอา worklog ขึ้น develop
  เพราะ `2-data.md` มี 17 บรรทัดที่อ้าง `.agents/`, Codex และคำสั่ง grep หา `Co-Authored-By`
  ซึ่งขัดกับที่ตัดสินไว้เองใน entry วันที่ 18 ก.ย.
- PR 795 บรรทัด เกินเพดาน ~400 ของทีม — เขียนเหตุผลไว้ในคำอธิบาย PR ว่าซอยไม่ได้เพราะ
  `HOW_TO_WORK.md` ชี้ไป `START_*.md` ทั้ง 3 ไฟล์ แยก PR แล้ว `check_doc_links` จะแดงระหว่างรอ merge

**บั๊กที่เจอใน `tools/` — ยังไม่แก้ เพราะเป็นของที่ทุกคนต้องเห็นชอบ**
- `tools/run_all_tests.py:142` ถือ pytest exit code 0 และ 5 เป็น `PASS`
  และเมื่อเครื่องไม่มี pytest จะขึ้นสถานะ `NO-PYTEST` แต่ยัง **exit 0**
- ผล: `check_all.py --with-tests` พิมพ์ "ผ่านทุกรายการ" ทั้งที่รัน test 0 ข้อ
  (พิสูจน์แล้ว: python 3.12 ที่ไม่มี pytest → `[ผ่าน] pytest ทุก service 0.21s`)
- รันด้วย `C:\ProgramData\miniconda3\Scripts\conda.exe run -n luma` จึงได้ของจริง: ผ่าน 24 test
  (backend 16 + database 8) — `conda` ไม่อยู่ใน PATH ของ git bash และ PowerShell ต้องเรียก path เต็ม
- repo ไม่มี `.github/workflows/` เลย ด่าน `check_all` จึงเป็นด่านเดียวที่กัน test พัง

**อัปเดตต่อ — รีวิวรอบ 4 แล้ว approve + merge #99**
- ตรวจที่ head `b8ec014` ใน worktree `pr99` (สะอาด · 0 behind develop) รัน test เองได้ 35 ข้อผ่าน ล้ม 0
- ตรวจเพิ่มที่รอบก่อนยังไม่ได้ดู: ไล่ `send_file(full_path)` ย้อนไปถึง `forge_client.save_base64_image()`
  พบว่าชื่อไฟล์เป็น `uuid4().hex + ".png"` ไม่มี input ของผู้ใช้ใน path เลย → **ไม่มีช่อง path traversal**
  · `max_per_page=100` · `icontains(q, autoescape=True)` · `page`/`per_page` เป็น `type=int` ส่งค่าขยะไม่ 500
- ยืนยันเหตุผลเรื่อง ownership ของ jet ด้วยของจริง ไม่ใช่เชื่อคำอธิบาย: `/api/generate` บน develop
  สร้าง `Asset(prompt=, file_path=)` ไม่ผูก `user_id` และ migration `deba60c08f36:34` ตั้ง `nullable=True`
  → เปิด filter ตอนนี้จะคืน 0 แถวเสมอ แกลเลอรีว่างทั้งระบบ **เปิดไม่ได้จริง**
- approve พร้อมบันทึก probe เรื่อง test tiebreaker ลงในรีวิว แล้ว merge เข้า develop สำเร็จ commit `331075c`
- develop หลัง merge รัน test ครบ: ผ่าน 35 (backend 27 + database 8) ล้ม 0 — DoD ข้อ "ระบบยังรันได้" ผ่าน
- PR body ไม่มี `Closes #100` GitHub จึงไม่ปิดเอง → ปิด #100 ด้วยมือพร้อมอ้าง commit
- เปิด **issue #115** ให้คนที่ 1 (`owner:1` `security` `priority:high`): `/api/generate` ผูก `user_id`
  → เปิด ownership filter → แล้วค่อย #97 `NOT NULL` · MUST ระบุว่าต้องตอบ 404 ไม่ใช่ 403 เมื่อไม่ใช่เจ้าของ
  และต้องตัดสินใจเรื่อง asset เก่าที่ `user_id` เป็น NULL ซึ่งบล็อก #97 ของเราอยู่
  · test tiebreaker ใส่เป็น MAY ใน #115 เพราะต้องแตะไฟล์ test ชุดเดียวกันอยู่แล้ว

**อัปเดตต่อ — แก้ขอบเขต #115/#97 + ฐานข้อมูลในเครื่องที่ค้าง 1 migration**
- เช็คฐานจริง `services/backend/instance/luma.db` พบว่าค้างที่ `18566175f613` (migration ตัวแรก)
  ทั้งที่ `deba60c08f36` merge ไปแล้วตั้งแต่ PR #96 → ไม่มีตาราง `users` ไม่มีคอลัมน์ `user_id`
  แปลว่าถ้ารันเว็บทดสอบ login จะพัง และทดสอบ #97 ไม่ได้เลยเพราะคอลัมน์ที่จะเปลี่ยนยังไม่มี
- ตอนรัน `flask db upgrade` ครั้งแรกไม่มีอะไรเกิดขึ้น **ต้นเหตุคือ working tree อยู่บน
  `feat/skeleton-assets-table` ที่ตามหลัง develop** ไฟล์ `deba60c08f36` จึงไม่มีอยู่ในดิสก์
  alembic เห็นแค่ migration ตัวเดียวจึงรายงานว่า `18566175f613 (head)` — ไม่ใช่บั๊ก alembic
  · checkout develop แล้วรันอีกครั้งจึงขึ้นเป็น `deba60c08f36` สำเร็จ (assets 0 แถว users 0)
  · **บทเรียน: งาน db ต้องทำจาก branch ที่ตัดจาก develop เท่านั้น ไม่ใช่จาก branch นี้**
- `PRAGMA foreign_keys` อ่านได้ 0 ตอนต่อด้วย `sqlite3` ตรงๆ — ตรวจแล้วไม่ใช่ปัญหา
  `app/models/__init__.py:63` มี event listener เปิด `PRAGMA foreign_keys=ON` ทุก connection
  และมี `test_every_connection_has_foreign_keys_pragma_on` คุมอยู่
- แก้ #115: ตัด MUST ข้อ "ตัดสินใจเรื่อง asset เก่าที่ user_id เป็น NULL" ออก เพราะวางผิดเจ้าของ
  `.github/CODEOWNERS` ระบุ `/services/database/ @boss2912` คนเดียว คนที่ 1 แตะ migration ไม่ได้
- คอมเมนต์ใน #97: ย้าย MUST ข้อนั้นมา · แก้ "รออะไรก่อน" ที่ล้าสมัย (#49/#50 merge แล้ว ตัวที่บล็อก
  จริงคือ #115 ข้อแรก) · เสนอ 3 ทางสำหรับแถวเก่าพร้อมผลต่าง **ยังไม่เคาะ รอตัดสิน**
  · ทาง A ที่แนะนำ: migration สร้างบัญชี demo แล้ว UPDATE แถว NULL ไปที่บัญชีนั้น
    เพราะ #31 ต้องมีเจ้าของให้ asset 20 ใบอยู่แล้ว และ downgrade กลับได้โดยข้อมูลไม่หาย

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. เคาะว่าจะใช้ทาง A/B/C กับแถวเก่าของ #97 แล้วเขียน test 3 ข้อก่อนเขียน migration
   (test เขียนได้เลยไม่ต้องรอ #115 — ตัวที่รอคือการเปลี่ยน `NOT NULL` จริง)
2. บอกคนที่ 3 เรื่อง 4 ข้อของ draft 8 ตัว และให้กด Ready for review
3. ตัดสินว่าจะเปิด issue เรื่องบั๊ก `run_all_tests.py` และเรื่อง CI ไหม
4. seed data ของ #31 — MUST 2 ข้อยังไม่เริ่ม · #17 tags many-to-many · #24 Asset Hub queries

**รออะไรจากใคร**
- คนที่ 1: รีวิว #110 และ #112 · รายละเอียด callback contract ของ #32 (ยังบล็อกตาราง `jobs`)
- คนที่ 3: กด Ready for review ทั้ง 8 ตัว

---

## 2026-09-20 (รอบ 2) · เคลียร์ของค้างในเครื่อง + รีวิว #99 รอบ 3 + เปิด PR #110

**branch**: `feat/skeleton-assets-table`, `feat/db-backup-restore` · **สถานะ**: PR #110 เปิดแล้ว · #99 รอบอสตัดสิน

**ทำอะไรไป**
- ตัด path ที่มีชื่อผู้ใช้ Windows ออกจาก worklog บรรทัด env (`check_no_secrets.py --all` เคยฟ้อง [FAIL] จุดนี้จุดเดียว) แล้ว commit + push worklog 19-20 ก.ย. ที่ค้างในเครื่อง 171 บรรทัด
- merge `origin/develop` เข้า `feat/db-backup-restore` (ตามหลัง 10 commit, ไม่มี conflict) → push → เปิด **PR #110** เข้า develop
  · ไม่ใส่ `Closes #31` เพราะ MUST 2 ข้อแรก (seed data) ยังไม่ทำ ปิด issue ไม่ได้
- รีวิว PR #99 รอบ 3 ที่ head `b8ec014` — jet push แก้ตั้งแต่ 19 ก.ย. 09:20 น. แล้ว PR ค้างอยู่ที่ฝั่งเราเอง ไม่ได้รอ jet

**ผลรีวิว #99 รอบ 3 (ไล่โค้ดจริง ไม่ได้ดูแค่ diff)**
- ข้อ 3 ที่ขอไว้ทำครบทั้ง 2 จุด: `test_list_assets_ordered_by_newest` เทียบ `prompts` ทั้ง list แล้ว
  และเพิ่ม `test_list_assets_tiebreaker_uses_id_when_created_at_equal`
- รัน `pytest` ใน worktree `pr99` ผ่าน 27 test
- **แต่ probe ด้วยการแก้โค้ดจริงแล้วพบว่า test tiebreaker ยังพิสูจน์ไม่ได้**:
  ลบ `Asset.id.desc()` ออกจาก `api.py:122` ให้เหลือ `order_by(created_at.desc())` → test **ยังผ่านทั้ง 11 ข้อ**
  (SQLite บังเอิญคืนแถวเรียง id มาก→น้อยเมื่อ created_at เท่ากัน)
  · สลับเป็น `Asset.id.asc()` → test fail จริง แปลว่า test จับ "ลำดับผิดทิศ" ได้ แต่จับ "tiebreaker หายไป" ไม่ได้
  · คืนไฟล์ด้วย `git checkout --` แล้ว worktree สะอาด
- โค้ดจริงถูกต้องอยู่แล้ว (`order_by(Asset.created_at.desc(), Asset.id.desc())`) — ที่อ่อนคือ test ไม่ใช่ behavior

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. บอสตัดสินว่า #99 จะ approve พร้อมหมายเหตุเรื่อง test sensitivity หรือขอแก้รอบ 3 (ผมยังไม่กดอะไรบน GitHub)
2. seed data ของ #31 — MUST 2 ข้อ ยังไม่เริ่ม (asset อย่างน้อย 20 ใบพร้อม tag, รันซ้ำได้ไม่ซ้ำข้อมูล)
3. `develop` ในเครื่องยังตามหลัง origin (ตอนเริ่ม session behind 50)
4. #17 tags many-to-many (priority:high) และ #24 Asset Hub queries ยังไม่เริ่ม

**รออะไรจากใคร**
- คนที่ 1: รายละเอียด callback contract ของ #32 (ยังบล็อกตาราง `jobs` ของ #16)

---

## 2026-09-20 · #32 วิเคราะห์ ownership ของ queue และ callback contract

**branch**: ไม่ได้แตะโค้ด · **สถานะ**: รอ backend owner ยืนยันรายละเอียด contract

**ทำอะไรไป**
- ตรวจ `docs/worklog/2-data.md`, `docs/API_CONTRACT.md` และ `docs/ARCHITECTURE.md` เทียบกับข้อความของ Dorij
- ยืนยันจากเอกสารว่า API ปัจจุบันกำหนดผลลัพธ์ AI เป็น `{ "images": ["<base64>"], "seed_used": ... }` แต่ยังไม่มี callback endpoint, token format, response code หรือ retry limit
- ร่างข้อความภาษาอังกฤษให้ Dorij โดยแยกข้อเท็จจริงออกจากข้อเสนอ: AI engine ถือ queue/worker, backend ถือการอ่านเขียน `jobs`, และ callback failure ต้อง retry โดยไม่ generate ภาพซ้ำ

**ตัดสินใจอะไรไว้**
- ยังไม่แก้ `API_CONTRACT.md` และยังไม่สร้าง migration `jobs` เพราะ callback URL, authentication, response codes, retry limit และที่เก็บภาพเมื่อ callback ล้มเหลวยังไม่ได้รับการยืนยันจาก backend owner
- ใช้รูปแบบ `images` array ให้สอดคล้องกับ contract ปัจจุบัน แทนการเพิ่ม `image_base64` เดี่ยวโดยไม่มีหลักฐานรองรับ

**ลองแล้วไม่ได้ผล**
- ค้นหา callback endpoint และ policy ใน repo แล้วไม่พบ; จึงไม่สามารถอ้างค่าเหล่านี้เป็นข้อตกลงเดิมได้

**ค้างอยู่ / ทำต่อจากตรงไหน**
- ให้คนที่ 1 ยืนยัน callback URL, token format, callback success status, retry limit และ storage/recovery policy ใน `API_CONTRACT.md`
- หลังยืนยันแล้ว ค่อยสร้าง/แก้ schema `jobs` และแจ้งคนที่ 3 ให้เริ่ม implementation queue/worker ตาม contract เดียวกัน

**รออะไรจากใคร**
- คนที่ 1: callback endpoint, authentication, response codes, retry limit และนโยบายเก็บภาพเมื่อ callback ล้มเหลว
- คนที่ 3 / Dorij: ยืนยันว่าจะ implement ตาม contract หลังรายละเอียดถูกบันทึก

---

## 2026-09-19 · ตอบคำถามพอร์ตของคนที่ 3 + ตรวจ Forge share (ไม่ได้แก้โค้ด)

**branch**: ไม่ได้แตะโค้ด · **สถานะ**: ย้ายไปทำต่อใน Codex (รายละเอียดส่งต่ออยู่นอก git)

**ทำอะไรไป**
- คนที่ 3 ถามว่า backend → ai-engine :8000 → Forge :7860 ใช่ไหม → ตอบว่าใช่ตามดีไซน์ (`ARCHITECTURE.md` §8)
  แต่โค้ดบน develop ขัดกับดีไซน์ 3 จุด: `config.py.example` ตั้ง `FORGE_AI_ENDPOINT` ซึ่งทำให้ backend ข้าม ai-engine ·
  `app/__init__.py:63` ตั้งค่าเริ่มต้น `AI_ENGINE_URL` เป็น :7860 · mock ให้บริการทั้งสอง API บนพอร์ตเดียว
- Forge (reForge ผ่าน StabilityMatrix) `--share` สร้าง link ไม่ได้ เพราะ Defender ลบ `gradio\frpc_windows_amd64_v0.2`
  ทุกครั้งที่เปิด (เห็นใน `Get-MpThreatDetection`) · `/sdapi/v1/*` ตอบ 404 เพราะไม่มี `--api`

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. ตัดสินว่าจะเอา `FORGE_AI_ENDPOINT` ออกจาก backend ไหม → ถ้าเอาออก ให้เปิด issue ให้คนที่ 1 · บันทึกพอร์ต 8000 ลง API_CONTRACT (#32 ข้อ 7)
2. Forge: บอสเลือก `--share` แล้วและตั้งข้อยกเว้น Defender เฉพาะไฟล์ frpc สำเร็จ
   · ค้างเพิ่ม `--api` แล้วตรวจ `/sdapi/v1/samplers` ผ่านลิงก์ `gradio.live` และตัดสินเรื่อง `--gradio-auth`/`--api-auth`
3. คิวเดิมจากรอบ 2 ของวันที่ 18 ยังไม่ได้ขยับเลย

**รออะไรจากใคร**
- คนที่ 1 + 3: ตกลงพอร์ตและชื่อ env var

**อัปเดตต่อ — รีวิว PR #99 รอบ 2**
- ตรวจ head `5aff042` เทียบกับ review รอบแรกและไล่โค้ดจริงครบ 5 ข้อ:
  ข้อ 2 (tiebreaker `created_at DESC, id DESC`), ข้อ 4 (escape `%`/`_`) และข้อ 5 (เพดาน `per_page=100`) แก้แล้ว
  · ข้อ 1 แก้แล้วเฉพาะกรณี **ไม่ login ต้องได้ 401** แต่ ownership ยังไม่มี — ผู้ใช้ที่ login แล้วยังเห็น
  `Asset.query` ทั้งตาราง ตั้งใจรอ #97 และ `/api/generate` บันทึก `user_id` ก่อน
- ข้อ 3 ยังไม่ครบ: `test_list_assets_ordered_by_newest` ตรวจแค่ `items[0]` จึงยังผ่านได้แม้ลำดับเป็น
  `[Newest, Oldest, Middle]` และยังไม่มี test กรณี `created_at` เท่ากันที่ต้องเรียง `id` มากก่อน
- รัน `python tools/check_all.py --with-tests` ผ่านทั้งหมด 34 test (backend 26 + database 8)
  และ probe พฤติกรรมเวลาเท่ากัน, wildcard `%`, เพดาน `per_page` ผ่านตามโค้ด
- ส่ง review แบบ `CHANGES_REQUESTED` แล้วเวลา 14:36 น. ที่ commit `5aff042` — ขอแก้เฉพาะ test การเรียง 2 จุดข้างบน
  · PR อยู่สถานะ `BLOCKED` · ร่าง review เก็บที่ `.agents/review-pr99.txt`

**ค้างจากรีวิว #99**
- รอ jet push แล้วรีวิวรอบ 3 เฉพาะ test ลำดับทั้งชุด + test เวลาเท่ากัน และตรวจว่าไม่มี regression เพิ่ม
- ห้ามติ๊ก `API_CONTRACT.md` ข้อ 2 จนกว่า ownership จะเสร็จ

**อัปเดตต่อ — ทำความเข้าใจ diff #31**
- ไล่เหตุผลของ `restore()` ที่ต้องเรียก `_check_ok(backup_file)` ก่อน `_copy()`:
  ถ้า copy ไฟล์เสียทับฐานข้อมูลจริงก่อน ฐานข้อมูลดีเดิมจะหาย แล้วตรวจเจอภายหลังก็ย้อนกลับไม่ได้
- อธิบายเหตุผลที่ `backup()` ใช้ `sqlite3.Connection.backup()` แทนการ copy ไฟล์ `.db` ตรง ๆ:
  SQLite เป็นคนสร้าง snapshot ที่สอดคล้องกัน แม้ Flask อาจกำลังเขียนอยู่ จึงไม่เสี่ยงได้ไฟล์ครึ่งเก่า–ครึ่งใหม่
- ยังไม่ได้ push branch `feat/db-backup-restore` และยังไม่ได้เปิด PR — commit ยังคงเป็น `45bc4cf`

**อัปเดตต่อ — ออกแบบ API_CONTRACT #32 ข้อ 3 (ยังรอทีมยืนยัน)**
- บอสเลือก `POST /api/generate` แบบ queued: ตอบ HTTP `202` พร้อม `{ "status": "queued", "job_id": 17 }`
  แล้ว frontend polling `GET /api/jobs/<job_id>` เพื่อตรวจ `pending → running → done/failed`
- แนวทาง implementation ที่เลือกคือ Python `queue.Queue` + worker 1 ตัว
  · ไม่ใช้ Redis, Celery หรือ WebSocket · service ดับกลางงานให้ job เป็น `failed` แล้วผู้ใช้กดใหม่ ไม่ทำ automatic resume
- ใช้ตัวอย่าง `Image-processing-workshop_V1` เทียบแล้ว: workshop เป็น synchronous และถ้า backend ดับกลาง request
  frontend จะ error/timeout แล้วต้องกดใหม่ จึงเก็บพฤติกรรม fail-and-retry แต่ไม่ลอกการรอแบบ synchronous มาใช้กับ LUMA
- ร่างข้อความภาษาไทยสำหรับ Jet (`@jet-work`) และภาษาอังกฤษสำหรับ Dorji (`@tsheringdorji`) แล้ว
  แต่ **ยังไม่ได้ส่งและยังไม่ถือว่าเป็นข้อตกลงทีม**

**ค้างจาก API_CONTRACT #32**
- ส่งข้อเสนอข้อ 3 ให้ Jet และ Dorji ยืนยันก่อน แล้วจึงบันทึกลง `docs/API_CONTRACT.md`
- ข้อ 6 ยังไม่ตัดสินว่า queue worker อยู่ service ไหน และใครเขียน/อ่านตาราง `jobs`
- ห้ามติ๊กข้อ 3 และห้ามสร้าง migration `jobs` จนกว่าคนที่ 1 และ 3 จะเห็นชอบ

---

## 2026-09-18 (รอบ 2) · #31 backup/restore + รีวิว PR ของคนที่ 1

**branch**: `feat/db-backup-restore` (worktree แยกที่ `Project_LUMA/luma-wt-backup/`) · commit `45bc4cf`
**สถานะ**: commit ในเครื่องแล้ว **ยังไม่ push / ยังไม่เปิด PR**

**ทำอะไรไป**
- `services/database/backup/db_backup.py` — `backup` / `restore` ผ่าน `sqlite3.Connection.backup()`
  ชื่อไฟล์ `luma-<UTC ถึงไมโครวินาที>.db` ไม่เขียนทับ · restore ตรวจ `PRAGMA integrity_check` ก่อนเขียนทับเสมอ
  · หา path ของ .db จาก `migrate_app` (ไฟล์เดียวกับ app จริง) · วิธีใช้อยู่หัวไฟล์
- `services/database/tests/test_backup_restore.py` — 5 test (round-trip นับแถวเท่าเดิม, ชื่อไม่ชน, ไม่มีไฟล์ต้นทาง,
  ไฟล์ขยะ, ไฟล์ SQLite เสียบางหน้า) · ทดลองทำโค้ดพังโดยตั้งใจ 4 แบบ test จับได้ครบ
- `services/database/README.md` ติ๊ก "สคริปต์ backup + คู่มือ restore"
- `check_all.py --with-tests` ผ่าน · database 12 + backend 12 test ผ่าน · รันคำสั่งจริง backup → ลบ → restore บน DB ชั่วคราวได้แถวครบ

**เจอระหว่างทำ (สำคัญ)**
- ⚠️ **backup API คัดลอกไฟล์ SQLite ที่เสียบางหน้าทับปลายทางได้เงียบๆ ไม่มี error** — ถ้า restore ไม่ตรวจก่อน DB ดีจะหาย
- test ที่ลบไฟล์ .db บน Windows ต้อง `db.engine.dispose()` หลัง `upgrade()` ไม่งั้น `WinError 32` (engine ถือไฟล์ค้าง)
- `print()` ภาษาไทยพังเมื่อ console/pipe เป็น cp1252 → ใช้ `_force_utf8_stdout()` แบบเดียวกับ `tools/check_all.py`
- **ตาราง `jobs` ยังไม่ควรทำ** — API_CONTRACT ข้อ 3 (sync/queued) และข้อ 6 (jobs ใครเขียน/อ่าน) ยังเป็น ⬜
  และ `ARCHITECTURE.md` วางคิวไว้ที่ ai-engine ขณะที่ข้อเสนอจากติวเตอร์วางที่ backend — ทำก่อนตกลง = migration ซ้ำ
- env ที่ใช้รัน test: `conda activate luma` (env อยู่ใน `.conda/envs/luma` ของเครื่องตัวเอง) มี flask/flask_migrate/pytest ครบ

**PR ของคนที่ 1**
- **#92 approve + merge แล้ว** (`faadcc7`) — ตรวจจากโค้ดจริง: เลิกเทียบ `"wrong-password"`, ใช้ `check_password_hash`,
  `register` ไม่หาย, ไม่มี trailer, check_all ผ่าน · ฝากไว้ใน review: ตอน V5 ต้องใส่ `ProxyFix`
  ไม่งั้น rate limit นับ IP ของ Nginx → คนหนึ่งกรอกผิด 5 ครั้ง ทุกคนโดนล็อก
- **#99 ขอแก้** — `GET /api/assets` ไม่ต้อง login ก็ได้ 200 (IDOR) · เรียงไม่มี `id` ตัดสินเวลาเท่ากัน ·
  test เรียงลำดับไม่ได้ทดสอบจริง · `ilike` ไม่ escape, `per_page` ไม่มีเพดาน · API_CONTRACT ข้อ 2 ติ๊ก ✅ เร็วไป
- #80 ไม่ได้แตะ — ไม่มี commit ใหม่หลังขอแก้ 5 ก.ย. (ถูกซอยเป็น #99 แล้ว)
- ⚠️ ยังไม่ได้ปิด issue #51 ของ #92 — ต้องปิดมือ (Closes ไม่ทำงานบน develop) แต่ยังไม่ได้ไล่ MUST ของ #51

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. อ่าน diff `45bc4cf` ให้เข้าใจเอง (โดยเฉพาะลำดับ `_check_ok` ก่อน `_copy` ใน `restore`) แล้วค่อย push + เปิด PR เข้า develop ใส่ `Refs #31` (seed ยังไม่เสร็จ)
2. ไล่ MUST ของ #51 แล้วปิด issue ถ้าครบ
3. ตกลง API_CONTRACT ข้อ 3, 5, 6 กับคนที่ 1 และ 3 → ปลดล็อก `jobs`, `tags`, seed
4. worktree รีวิว `pr92`, `merge99` ลบแล้ว · ยังมี worktree เก่า `wt2` (detached, prunable) จาก session ก่อน — ลบได้ด้วย `git worktree prune`

**รออะไรจากใคร**
- คนที่ 1: แก้ #99
- คนที่ 1 + 3: API_CONTRACT ข้อ 3, 5, 6

---

## 2026-09-18 · ตรวจโปรเจกต์เทียบสเปกอาจารย์ (ไม่ได้แก้โค้ด)

**branch**: ไม่ได้แตะ · **สถานะ**: ได้รายการงาน + คำถามที่ต้องถามอาจารย์

**ทำอะไรไป**
- โหลดรูป LUMA 1-3 จากโพสต์อาจารย์ (7 ก.ค.) → ตรงกับ Lecture 4 หน้า 54–56 ที่ repo สรุปไว้แล้ว
  รูป LUMA 2 คือ "แบ่งหน้าที่**ในกลุ่ม**" → ทุกกลุ่มสร้างระบบของตัวเองครบ โครง repo ไม่หลุด
- คุยกับติวเตอร์ Iris 8 รอบ, C 8 รอบ, Sena 3 รอบ · สรุปเต็มอยู่นอก repo:
  `Project_LUMA/{iris,c,sena}_chat_2026-09-18/00_สรุป.md`
  ⚠️ ติวเตอร์ทั้ง 3 ไม่มีสไลด์วิชาเลย และยอมทุกข้อที่โดนแย้ง → ใช้เป็นความรู้ทั่วไป ไม่ใช่ข้อยืนยัน
  ตัวเลขคะแนน/เวลา/ผลทดลองที่ติวเตอร์ให้ = แต่งขึ้นทั้งหมด ห้ามใช้
- Sena (ตรวจอิสระ ไม่เห็นข้อสรุปคนอื่น) ได้ข้อสรุปตรงกันว่า รันข้าม 3 เครื่องจริง = หัวใจ · Queue จำเป็น
  · ต้องดึงงานกลุ่ม Lecture 10 เข้า repo · แผน 17 วันของ Sena ให้คนที่ 2 ทำ migration tags + jobs (สัปดาห์นี้)
  และ dashboard + backup (สัปดาห์หน้า) — ยังไม่ได้ตกลงทีม
- อ่านสไลด์ Lecture 8–11 เอง เจอว่า **Lecture 10 Workshop = segmentation ≥50 ภาพ + ground truth + morphology
  วัดด้วย Confusion Matrix + ROC** → คือวิธีที่อาจารย์ใช้วัดผล segmentation และทีมทำไว้แล้วใน
  `310-3311_Image_Processing/Image-processing-workshop_V2/` (ยังไม่ได้เปิดโค้ด) · Lecture 11 สอน K-Means, watershed
  · Lecture 9 สอน region labeling/contour + Workshop REST server

**เจอว่าหลุดจากสเปก / ยังไม่มี**
- `COURSE_REQUIREMENTS.md` สรุปถึง Lecture 7 แต่อาจารย์สอนถึง Lecture 11 แล้ว (Mediapipe, Edge/Corner, Morphological, Segmentation)
- สเปก LUMA 2 ที่ยังไม่มีเลย: **Queue** (ตอนนี้ `/api/generate` บล็อกได้ 120 วิ), Image Editing/img2img, Model/LoRA, คู่มือ, Dashboard, Backup
- สเปก Lecture 4 หน้า 52 ที่ยังไม่มี: Smart Canvas จัด Layout + เลือกวัตถุอัตโนมัติ, Asset Hub ปรับ style ต่อผู้ใช้
- 🐛 `frontend/js/register.js` ยังคอมเมนต์ fetch ไว้ และ path เป็น `/api/register` (ของจริง `/api/auth/register`) — ของคนที่ 1

**ตัดสินใจอะไรไว้** (ข้อเสนอ ยังไม่ได้ตกลงทีม)
- remove_bg ใช้ HSV จากการบ้าน 5.2 ไม่ใช้ `rembg` · ไม่ใช้ API ภาพภายนอกแทน Forge
- 05_evaluation วัด segmentation ด้วย Confusion Matrix + ROC ตาม Lecture 10 (+ Precision/Recall/F1/IoU) กับชุดภาพที่มี ground truth · histogram stats ย้ายไป 04_features
- เก็บไฟล์ภาพที่ .20 ที่เดียว · ภาพจาก Forge มาเป็น base64 ใน response อยู่แล้ว

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. ถามอาจารย์: วันส่ง (ก่อน/หลังสอบ 5–16 ต.ค.) · แยก 3 เครื่องจริงหรือจำลองได้ · เกณฑ์คะแนน
2. คิวของผมยาวขึ้น: migration `jobs` (Queue รอตัวนี้ · ⛔ รอ API_CONTRACT ข้อ 3, 6 — ดูรอบ 2) → `tags` + `asset_tags` (ยังรอข้อ 5 API_CONTRACT) → คอลัมน์ `assets.source` → query Asset Hub (#24) → seed + backup (#31 ส่วน backup ทำแล้วในรอบ 2)
3. ไล่ Lecture 8–11 หาข้อกำหนดใหม่ แล้วเปิด PR แก้ `COURSE_REQUIREMENTS.md`

**รออะไรจากใคร**
- อาจารย์: 3 ข้อข้างบน
- คนที่ 3: พร้อมทำ ai-engine ไหม มี GPU ไหม · ข้อ 5 API_CONTRACT (รูปแบบ auto-tag)
- คนที่ 1: register.js · #100 #101

---

## 2026-09-09 (รอบ 6) · เคลียร์ PR ของคนที่ 1 และเจอช่องโหว่ frontend ขึ้นก่อน backend

**branch**: ทำบน GitHub ล้วน · **สถานะ**: เหลือ #92 กับ #80

**merge เข้า develop รอบนี้**
- #84 blueprints + error handlers · #85 logging · #88 generate endpoint
- #89 gallery UI (แก้ #94 ให้ในตัว — คืน fallback `""` ใน layout.js)
- #91 login/register ของจริง · #98 gitignore ของ Claude Code
- **#96 ของเราเอง jet เป็นคนรีวิวและ merge ให้** ตาราง users อยู่บน develop แล้ว
- jet ปิด #82 กับ #90 เอง

**คนที่ 1 เขียน auth ใหม่จริง — ผ่านหมด**
`User.query.filter_by(email=...)` + `check_password_hash` · error เดียวกันทั้งกรณีไม่เจอ user
และรหัสผิด · เก็บแค่ `session["user_id"]` · `/me` เช็คกรณี user ถูกลบ · อีเมล `.strip().lower()`
ตรงกันทั้ง register/login · test สมัครจริงแล้ว login ด้วยรหัสที่สมัคร + เคสรหัสผิด/อีเมลไม่เคยสมัคร

**⛔ ช่องโหว่ที่เจอ — merge frontend ขึ้นไปโดย backend ยังไม่มี**

| หน้า (merge แล้ว) | เรียก endpoint | มีบน develop |
|---|---|---|
| `gallery.js` (#89) | `GET /api/assets` | ไม่มี |
| `canvas.js` (#93) | `POST /api/pipeline/palette/extract` | ไม่มี |
| `canvas.js` (#93) | `POST /api/pipeline/segmentation/remove_bg` | ไม่มี |

หน้า gallery กับ canvas **เปิดแล้ว 404 อยู่ตอนนี้**
สาเหตุ: ตอนรีวิว #89 #93 ดูแต่ว่าโค้ด frontend ถูกไหม ไม่ได้เช็คว่า endpoint ที่มันยิงมีจริงหรือยัง
→ **บทเรียน: รีวิว PR frontend ต้อง grep หา `fetch(` แล้วเทียบกับ route ที่มีจริงบน develop เสมอ**

เปิด #100 (assets endpoints) และ #101 (pipeline endpoints) ตามเก็บ แล้วคอมเมนต์ผูกไว้ที่
#58 #60 #61 ว่ายังปิดไม่ได้ และที่ #80 ว่าเหลืออะไรบ้าง (29/37 ไฟล์ขึ้นไปแล้ว)

**เรื่องที่ต้องรู้ (จดไว้กันลืม)**

- ⚠️ **`Closes #NN` ใน PR ไม่เคยทำงานเลยในโปรเจกต์นี้** GitHub ปิด issue อัตโนมัติเฉพาะตอน
  merge เข้า **default branch (`main`)** เท่านั้น ของเรา merge เข้า `develop` ทั้งหมด
  ผลดี: #82 ไม่ได้ปิด #45 ของเราอย่างที่กังวลไว้ · ผลเสีย: **ทุก issue ต้องปิดมือเอง**
  `AGENTS.md` ข้อ 4 ที่เขียนว่าให้ใส่ `Closes #NN` จึงให้ผลไม่ตรงกับที่เขียนไว้ ควรแก้เป็น
  `Refs #NN` แล้วปิด issue เองหลัง merge

- ⚠️ **regex สแกนร่องรอย AI ต้องยึดหัวบรรทัด ไม่ใช่หาคำลอยๆ**
  ผมใช้ `claude|anthropic|co-authored` แล้วรายงานผิดว่า #98 กับ #91 มี attribution ติดมา
  ความจริงมันไปจับคำว่า claude ใน path `.claude/settings.local.json` กับในประโยคอธิบาย
  คนที่ 1 ทักกลับมาและเขาถูก เกณฑ์ที่ถูกคือ
  `git log origin/develop..HEAD --format=%B | grep -E "^(Co-Authored-By:|Claude-Session:)"`
  บทเรียนซ้อน: ตอนสแกนผมใช้ข้อมูลเก่าค้างในมือด้วย (#91 ถูกล้างไปแล้ว hash เปลี่ยนหมด)
  → ต้อง `git fetch` แล้วดึง head ใหม่ก่อนสแกนทุกครั้ง

- คนที่ 1 ตั้งค่าปิด attribution ได้แล้วผ่าน `.claude/settings.local.json`
  (`includeCoAuthoredBy: false`) และเพิ่มบรรทัดนั้นใน `.gitignore` ผ่าน #98
  ที่ขึ้น develop ไปแล้ว 2 คอมมิต (`b0b0907` `dd56782`) ตกลงกันว่าไม่ rewrite ย้อนหลัง

**ค้างอยู่ / ทำต่อจากตรงไหน**
1. **#92** โค้ดผ่านแล้ว เหลือ 2 อย่าง: ดึง develop แก้ conflict `auth.py`
   (ระวัง `def register` หาย เพราะไฟล์ใน #92 ไม่มีตัวนี้ ต้องยึดของ develop เป็นฐาน)
   และล้าง trailer ใน `d864d5e` กับ `09c4339`
2. **#80** รอคนที่ 1 ซอย `GET /api/assets` ออกมาเป็น PR ตาม #100 (ด่วนสุด gallery พังอยู่)
3. **#101** ต้องคุย 3 คน — request/response ของ pipeline endpoints ยังไม่มีใน API_CONTRACT
4. **ข้อ 2 ของ API_CONTRACT.md ยังเป็น ⬜** (GET /api/assets รับ param อะไร) ต้องเคาะก่อนเขียน #100
5. `feat/users-table` merge เข้า develop แล้ว ลบ branch ในเครื่องได้
6. `feat/skeleton-assets-table` ยังมีคอมมิตค้างไม่ push (เอกสารทีม + worklog ทั้งหมด)
7. `backup/pre-strip-agents` สำรอง ห้าม push

**รออะไรจากใคร**
- คนที่ 1: #92 · ซอย #80 ตาม #100 · คนที่ 3: ฟังก์ชัน pipeline ตาม #101

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

**เจอเพิ่มในโค้ดที่ merge ไปแล้ว (#83) — ยังไม่ได้เปิด issue**

`services/backend/app/__init__.py:32`
```python
SECRET_KEY="luma-dev-secret-key-change-in-production",
```
repo เป็น public ใครก็อ่านบรรทัดนี้ได้ ถ้า deploy แล้วลืมสร้าง `instance/config.py`
ระบบจะเซ็น session cookie ด้วย key ที่เห็นกันทั้งอินเทอร์เน็ต = ปลอม session เป็นใครก็ได้
ตรงกับที่ `instance/config.py.example` บรรทัด 12-13 เตือนไว้เองว่า v1 เคยทำ SECRET_KEY
หลุดขึ้น GitHub มาแล้ว (F09 ใน `archive/SECURITY_FIXES_v1.md`)

`services/backend/app/__init__.py:40-43`
```python
try:
    app.config.from_pyfile("config.py", silent=True)
except Exception:
    pass
```
`silent=True` จัดการกรณีไฟล์ไม่มีอยู่แล้ว ส่วน try/except ที่ครอบอีกชั้นกลืน error อื่นหมด
เคสจริง: `instance/config.py` พิมพ์ผิด -> SyntaxError -> ถูกกลืน -> ระบบรันต่อด้วย
SECRET_KEY ตัว default และชี้ฐานข้อมูล dev กว่าจะรู้ก็ตอนข้อมูลหาย

**ทางแก้ที่เสนอไป** (ส่งให้คนที่ 1 ทางแชทแล้ว ยังไม่ได้เปิด issue):
```python
app.config.from_mapping(
    SECRET_KEY=os.environ.get("LUMA_SECRET_KEY"),
    ...
)

# ไม่ครอบ try/except — config พังต้องรู้ทันที
app.config.from_pyfile("config.py", silent=True)

if config_overrides:
    app.config.update(config_overrides)

if not app.config.get("SECRET_KEY"):
    if app.config.get("TESTING"):
        app.config["SECRET_KEY"] = "testing-only-not-for-production"
    else:
        raise RuntimeError("ไม่พบ SECRET_KEY — ตั้ง env LUMA_SECRET_KEY หรือสร้าง instance/config.py")
```
ต้องคง fallback ฝั่ง TESTING ไว้ เพราะ `test_config.py` กับ `test_security.py`
เรียก `create_app({"TESTING": True, ...})` โดยไม่ส่ง SECRET_KEY มาด้วย

เสนอให้คนที่ 1 เอาไปรวมกับ PR ที่กำลังแก้ conflict อยู่แล้ว (#84 หรือ #92)
ไม่ต้องเปิด PR ใหม่ เพราะทั้งคู่แก้ไฟล์นี้อยู่แล้ว

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
