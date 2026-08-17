# LUMA v1 — สรุปสถาปัตยกรรมและบทเรียน (ก่อนรีเซ็ตโครงสร้าง)

> เอกสารนี้สรุป **สิ่งที่ v1 ทำได้จริง / ทำงานอย่างไร / อะไรควรหยิบกลับมาใช้**
> โค้ดคำต่อคำอยู่ใน [`CODE_SNAPSHOT_v1.md`](CODE_SNAPSHOT_v1.md)
> โค้ดใน git อยู่ที่ tag `backup/pre-restructure-develop`

**สถานะตอนถูกเก็บ**: รวม PR #10 + #11 + #12 เข้าด้วยกันแล้ว · `pytest` **33/33 ผ่าน** (บนฐานข้อมูลใหม่)

---

## 1. v1 คืออะไร

Flask monolith ชั้นเดียว ทำงานได้ครบวงจร: สมัคร → ล็อกอิน → พิมพ์ prompt → ยิงไป Stable Diffusion WebUI (Forge) → เก็บภาพ + แถวใน SQLite → แสดงใน gallery → ลบได้

เทียบกับ milestone ของอาจารย์ (Lecture 4 p.103) v1 อยู่ที่ **ปลาย V3** แล้ว:

| Milestone | สถานะใน v1 |
|---|---|
| V1 All-in-one Flask | ✅ |
| V2 Flask + SQLite | ✅ |
| V3 Flask + Forge | ✅ |
| V4 Separate Frontend | ❌ (template ยัง render จาก Flask) |
| V5 Nginx all Service | ❌ |

---

## 2. โครงสร้างไฟล์เดิม

```
luma-webapp/
├── run.py                     entry point (debug/host คุมด้วย env var)
├── requirements.txt
├── environment.yml            conda env "luma"
├── INSTALL.md · CONTRIBUTING.md
├── instance/
│   ├── config.py.example      ← template (config.py จริงถูกถอดออกจาก git)
│   └── luma.db                ⚠️ ถูก commit ขึ้น git โดยไม่ควร
├── app/
│   ├── __init__.py            create_app() factory
│   ├── models.py              User · Asset · Job
│   ├── routes/{main,auth,api}.py
│   ├── templates/             base · index · dashboard · auth/{login,register}
│   ├── static/css/style.css   dark theme, CSS variables
│   └── utils/logger.py        RotatingFileHandler
└── tests/                     7 ไฟล์ · 33 tests
```

---

## 3. Application Factory — แพตเทิร์นที่ควรเก็บไว้

`create_app(config_overrides=None)` ทำ 5 ขั้นตามลำดับ:

1. `app.config.from_pyfile("config.py", silent=True)` — `silent=True` สำคัญ เพราะ `config.py` ไม่ถูก track ใน git แล้ว เครื่องที่เพิ่ง clone หรือ test runner จะยังไม่มีไฟล์นี้ ต้องทำงานต่อได้ด้วยค่า default ไม่ใช่ crash ตอน import
2. `setdefault()` ค่า config ทุกตัว → มี fallback เสมอ
3. `config_overrides` — **พารามิเตอร์นี้คือสิ่งที่ทำให้เขียน test ได้** (in-memory SQLite + ปิด CSRF ต่อ test) ถ้าไม่มี จะต้องพึ่งไฟล์ config จริงตอนรัน test
4. ผูก extensions: `db` · `login_manager` · `migrate` · `csrf`
5. ลงทะเบียน blueprint แล้ว `db.create_all()`

> **บทเรียน**: `config_overrides` เป็นสิ่งที่ต้องมีตั้งแต่วันแรกในโครงใหม่ ไม่ใช่เพิ่มทีหลัง

---

## 4. Database Models

```python
User   id · username · email · password_hash · avatar_url · last_login_at · created_at
Asset  id · user_id(FK) · filename · prompt · tags · created_at
Job    id · user_id(FK) · prompt · status · result_asset_id(FK) · created_at
```

- `User.assets` = relationship + `backref="owner"`
- `Job.status` ∈ `pending` / `running` / `done` / `failed` — ตารางถูกสร้างไว้แต่ **ยังไม่มีโค้ดไหนใช้จริง** (ไม่มี queue) เป็นโครงรอไว้
- `tags` เป็น `String(255)` เก็บ comma-separated เช่น `"portrait,anime,4k"` — **ออกแบบไม่ดี** ค้นหาแบบ `LIKE '%tag%'` แล้ว match ผิด (`"art"` จะไป match `"artist"`) โครงใหม่ควรแยกเป็นตาราง `tags` + `asset_tags` (many-to-many)
- ⚠️ `datetime.utcnow()` ถูก deprecate แล้ว → โครงใหม่ใช้ `datetime.now(datetime.UTC)`

### `load_user`
```python
return db.session.get(User, int(user_id))   # ไม่ใช่ User.query.get() ที่ deprecated ใน SQLAlchemy 2.x
```

---

## 5. API Endpoints

| Method | Path | Auth | หมายเหตุ |
|---|---|---|---|
| GET | `/` | – | หน้าแรก |
| GET | `/dashboard` | ✅ | generate form + gallery |
| GET/POST | `/auth/register` | – | error รายฟิลด์ |
| GET/POST | `/auth/login` | – | rate limit 5 ครั้ง/60 วิ |
| **POST** | `/auth/logout` | ✅ | POST-only (ดู F15) |
| POST | `/api/generate` | ✅ | รับ prompt + 5 พารามิเตอร์ |
| GET | `/api/assets` | ✅ | list ของ user ตัวเอง |
| GET | `/api/assets/<id>/image` | ✅ | เสิร์ฟภาพ + เช็ค ownership |
| DELETE | `/api/assets/<id>` | ✅ | ลบไฟล์ + แถว DB |

### พารามิเตอร์ `/api/generate` (Issue #5)

| ตัว | ชนิด | ขอบเขต | default |
|---|---|---|---|
| `prompt` | str | ต้องมี, ไม่ว่าง | – |
| `negative_prompt` | str | – | `""` |
| `steps` | int | 1–50 | 20 |
| `cfg_scale` | int/float | 1–30 | 7 |
| `width` / `height` | int | 512 / 768 / 1024 เท่านั้น | 512 |

**ตรงกับที่อาจารย์สอน** — Lecture 2 p.10 แนะนำ CFG 8–14, steps 20–60 → โครงใหม่ควรตั้ง default CFG เป็น 8 ไม่ใช่ 7 และเพิ่ม `sampler_name` + `seed` ที่ v1 ยังไม่รับ

**ข้อควรระวังที่เจอ**: `isinstance(x, int)` ผ่านสำหรับ `bool` ด้วย (`True` เป็น `int` ใน Python) โค้ด v1 จึงต้องเช็ค `not isinstance(steps, bool)` ควบคู่ไปด้วย — อย่าลืมในโครงใหม่

---

## 6. ที่เก็บไฟล์ภาพ — จุดที่เปลี่ยนสำคัญที่สุด

**เดิม (v1 ต้น)**: `app/static/generated/` → Flask เสิร์ฟให้ใครก็ได้ที่รู้ URL ไม่ต้องล็อกอิน = **IDOR**

**หลังแก้**: `app/generated/` (นอก `static/`) + ดูได้ผ่าน `/api/assets/<id>/image` ที่เช็ค ownership เท่านั้น

path คิดจากตำแหน่งไฟล์ ไม่ใช่ cwd:
```python
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "generated"))
```
> เดิมใช้ `os.path.join("app", "static", "generated")` ซึ่งเป็น relative path พึ่ง current working directory — รันจากโฟลเดอร์อื่นแล้วหาไฟล์ไม่เจอ

### `_get_owned_asset_or_404()`
ตอบ **404 ไม่ใช่ 403** ทั้งกรณี "ไม่มี asset นี้" และ "มีแต่ไม่ใช่ของเรา" — ไม่บอกผู้โจมตีว่า id นั้นมีจริงหรือเปล่า

---

## 7. CSRF

```python
csrf = CSRFProtect()      # เปิดใช้ทั้งแอป
csrf.exempt(api_bp)       # ยกเว้น /api/* เพราะเป็น JSON ล้วน
```

เหตุผลที่ยกเว้น `/api/*` ได้อย่างปลอดภัย: ฟอร์ม HTML ธรรมดายิง `Content-Type: application/json` ไม่ได้ และ `DELETE` ไม่ใช่ simple method ตาม Fetch spec ต้องผ่าน CORS preflight ก่อน — เว็บนี้ไม่ตั้ง CORS ให้ origin อื่นเลย เบราว์เซอร์จึงบล็อก cross-site ไว้ตั้งแต่ preflight

> ฟอร์ม HTML จริง (login / register / logout) ยังบังคับ `csrf_token` ตามปกติ

---

## 8. JSON vs HTML บน 401

```python
@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith("/api/"):
        return jsonify({"error": "unauthorized ..."}), 401
    return redirect(url_for("auth.login", next=request.path))
```

เดิม Flask-Login redirect ไปหน้า login (HTML) เสมอ ทำให้ `fetch()` ฝั่ง JS พยายาม parse HTML เป็น JSON แล้ว error อธิบายไม่ได้

---

## 9. Rate limiting

in-memory `defaultdict(list)` เก็บ timestamp — 5 ครั้ง / 60 วินาที ตอบ **429**

**key ด้วย email ที่พยายามล็อกอิน ไม่ใช่ IP** — ถ้า key ด้วย IP คนที่ใช้ network เดียวกัน (network มหาลัย) จะโดนบล็อกไปด้วยทั้งที่ไม่เกี่ยว

⚠️ **ข้อจำกัด**: เก็บใน memory ของ process เดียว ถ้า deploy หลาย worker แต่ละตัวนับแยกกัน → V5 ที่มี Nginx + หลาย worker ต้องย้ายไป Redis หรือใช้ `Flask-Limiter`

---

## 10. Logging

`setup_logging(app)` ใน `create_app()`:
- console handler: `DEBUG` ถ้า `app.debug` ไม่งั้น `INFO`
- file handler: `RotatingFileHandler("logs/luma.log", maxBytes=1MB, backupCount=3)` เก็บเฉพาะ `WARNING`+
- `root_logger.handlers.clear()` ก่อนเพิ่ม กัน handler ซ้ำเวลา `create_app()` ถูกเรียกหลายครั้ง (สำคัญมากตอน test ที่สร้าง app ใหม่ทุก fixture)

---

## 11. Test suite (33 tests)

| ไฟล์ | ครอบคลุม |
|---|---|
| `conftest.py` | fixtures: `app` · `client` · `mock_forge_success` + helper `register/login/register_and_login` |
| `test_auth.py` | สมัคร/ล็อกอิน/ออก, password policy, rate limit, open redirect |
| `test_models.py` | ฟิลด์ใหม่ Issue #2, password hashing |
| `test_assets.py` | list assets, แยกตาม user |
| `test_assets_delete.py` | ลบ asset, ownership, 404 |
| `test_generate_params.py` | ขอบเขตพารามิเตอร์ Issue #5 |
| `test_e2e_flow.py` | ไหลครบ สมัคร→ล็อกอิน→generate→ดู→ลบ |
| `test_system_check.py` | ⚠️ สคริปต์เช็คแบบเก่า (ดูข้อ 12) |

**เทคนิคที่ควรเก็บ** — mock Forge AI ด้วย PNG 1×1 base64 ทำให้รัน test ได้โดยไม่ต้องเปิด Stable Diffusion จริง:
```python
TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
```

---

## 12. ปัญหาที่พบตอนตรวจ v1 (ต้องไม่เกิดซ้ำในโครงใหม่)

### ⚠️ ปัญหา A — `instance/luma.db` ถูก commit ขึ้น git
`.gitignore` มีบรรทัด `instance/*.db` อยู่แล้ว แต่ไฟล์ถูก commit **ก่อน** ที่กฎจะถูกเพิ่ม → git ยัง track ต่อไป

**ผลที่เกิดขึ้นจริง**: `test_system_check.py` ล้ม 3 ข้อ เพราะ schema ในไฟล์เก่าไม่มี `users.avatar_url`, `users.last_login_at`, `jobs.prompt` ที่ PR #12 เพิ่มเข้ามา และ **`db.create_all()` ไม่ ALTER ตารางที่มีอยู่แล้ว** — สร้างแค่ตารางที่ยังไม่มี

พอลบไฟล์ออกแล้วรันใหม่: **33/33 ผ่านทันที**

**สิ่งที่ต้องทำในโครงใหม่**:
- ไม่ commit ไฟล์ `.db` เด็ดขาด (`git rm --cached` ถ้าหลุดไป)
- ใช้ **Flask-Migrate จริงจัง** (`flask db migrate` / `upgrade`) ไม่พึ่ง `db.create_all()` เวลา schema เปลี่ยน
- `.gitignore` ครอบ `*.db` ทุกที่ ไม่ใช่แค่ `instance/`

### ⚠️ ปัญหา B — `pip install -r requirements.txt` พังบนเครื่อง locale ไทย
`requirements.txt` เป็น UTF-8 และมีคอมเมนต์ภาษาไทย แต่ pip อ่านด้วย locale codec ของเครื่อง (`cp874` บน Windows ไทย) →
```
UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 ... decoding with 'cp874' codec failed
```
ต้องตั้ง `PYTHONUTF8=1` ก่อนถึงจะติดตั้งได้

**สิ่งที่ต้องทำในโครงใหม่**: `requirements.txt` ใช้ **ASCII เท่านั้น** ย้ายคำอธิบายภาษาไทยไปไว้ใน `INSTALL.md`

### ⚠️ ปัญหา C — `datetime.utcnow()` deprecated
โยน `DeprecationWarning` 71 ครั้งตอนรัน test → ใช้ `datetime.now(datetime.UTC)`

### ⚠️ ปัญหา D — `test_system_check.py` ไม่ใช่ test จริง
เป็นสคริปต์ที่รันตอน **import** (โค้ด top-level) แล้วมี `test_all_checks_passed()` ตัวเดียวมา assert ตัวนับรวมท้ายสุด ผลคือ:
- ล้มข้อไหนก็บอกแค่ "3 checks failed" ไม่ระบุว่าข้อไหน จนกว่าจะอ่าน stdout
- ทำ `os.chdir()` ตอน import → กระทบ test ไฟล์อื่นที่รันตามมา
- ไม่ใช้ fixture เลย ต่อฐานข้อมูลจริงในเครื่อง

โครงใหม่ควรเขียนเป็น test แยกข้อตามปกติ ไม่เอาแพตเทิร์นนี้ไปใช้

### ⚠️ ปัญหา E — `tags` เป็น comma-separated string
ค้นหาแล้ว match ผิด → แยกตารางแบบ many-to-many (ดูข้อ 4)

### ⚠️ ปัญหา F — `Job` มีตารางแต่ไม่มีใครใช้
สเปกอาจารย์ระบุ "Queue" เป็นงานคนที่ 3 — v1 สร้างตารางรอไว้แต่ `/api/generate` ยังยิงตรงแบบ synchronous (บล็อก 120 วินาที) โครงใหม่ต้องทำ queue จริง

---

## 13. สรุป: อะไรควรหยิบกลับมาใช้

### ✅ เอาไปใช้เลย
- `create_app(config_overrides=...)` แพตเทิร์นเต็มรูปแบบ
- ชุด security fix ทั้ง 15 ข้อ → ดู [`SECURITY_FIXES_v1.md`](SECURITY_FIXES_v1.md)
- `_get_owned_asset_or_404()` + การเสิร์ฟภาพผ่าน route ที่เช็ค ownership
- `@login_manager.unauthorized_handler` แยก JSON/HTML
- `mock_forge_success` fixture + PNG 1×1
- `setup_logging()` พร้อม `handlers.clear()`
- CSS variables + dark theme ใน `style.css`

### ♻️ เอาไปใช้แต่ต้องแก้
- rate limiter → ย้ายไป Redis/Flask-Limiter สำหรับ V5
- `tags` → many-to-many
- `datetime.utcnow()` → `datetime.now(datetime.UTC)`
- default `cfg_scale` 7 → 8 (ตาม Lecture 2 p.10)

### ❌ อย่าเอาไป
- `test_system_check.py` (ดูปัญหา D)
- commit ไฟล์ `.db`
- คอมเมนต์ภาษาไทยใน `requirements.txt`
- `db.create_all()` เป็นวิธีจัดการ schema หลัก

---

## 14. สิ่งที่ v1 ยังไม่มีเลย และเป็นข้อกำหนดของอาจารย์

โครงใหม่ต้องเพิ่ม — ดูรายละเอียดใน [`../docs/COURSE_REQUIREMENTS.md`](../docs/COURSE_REQUIREMENTS.md)

1. **Image Processing pipeline 5 ส่วน** (Lecture 1 p.6) — ไม่มีแม้แต่โมดูลเดียว นี่คือเกณฑ์ให้คะแนนโครงงานหลัก
2. **Smart Canvas** — layout, color palette, background removal, segmentation
3. **Asset Hub** ที่ค้นหาได้จริง
4. **img2img / ControlNet / LoRA / Regional Prompt**
5. **Evaluation / metrics** — วัดประสิทธิภาพระบบ
6. **Nginx reverse proxy** + แยก frontend (V4/V5)
7. **Job queue** จริง
