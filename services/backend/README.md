# backend/ — Flask API Server

👤 คนที่ 1 — Web Platform (บอส)
**เครื่อง**: 192.168.1.20 (ตัวอย่าง) · **พอร์ต**: 5000

## หน้าที่

รับ request จาก frontend → ตรวจสิทธิ์ → เรียก `database/` และ `ai-engine/` → ตอบ JSON

## โครงสร้างที่ตั้งใจไว้

```
backend/
├── run.py                 entry point (debug/host จาก env var เท่านั้น)
├── requirements.txt       ASCII only
├── app/
│   ├── __init__.py        create_app(config_overrides=None)
│   ├── routes/            Blueprint แยกตามหน้าที่ (main / auth / api)
│   ├── models/            SQLAlchemy models
│   ├── services/          business logic — ตัวกลางระหว่าง route กับ ai-engine/db
│   ├── utils/             logger และของใช้ร่วม
│   ├── templates/         Jinja2 (V1-V3 เท่านั้น — ย้ายไป frontend/ ตอน V4)
│   └── static/            (V1-V3 เท่านั้น)
├── instance/              config.py จริง — ⛔ ห้าม commit (มีแค่ config.py.example)
└── tests/
```

## สิ่งที่ต้องทำตั้งแต่ commit แรก

จาก `archive/ARCHITECTURE_v1.md` และ `archive/SECURITY_FIXES_v1.md`:

- [ ] `create_app(config_overrides=None)` — **พารามิเตอร์นี้คือสิ่งที่ทำให้เขียน test ได้**
      ต้องมีตั้งแต่วันแรก ไม่ใช่เพิ่มทีหลัง
- [ ] `app.config.from_pyfile("config.py", silent=True)` + `setdefault()` ทุกค่า
- [ ] `CSRFProtect` เปิดใช้ **พร้อมกับ** ใส่ `csrf_token()` ในเทมเพลตใน commit เดียวกัน (F06)
- [ ] `@login_manager.unauthorized_handler` แยก JSON 401 สำหรับ `/api/*` (F10)
- [ ] `debug` / `host` จาก env var `LUMA_DEBUG` / `LUMA_HOST` (F02)
- [ ] `setup_logging()` ที่เรียก `root_logger.handlers.clear()` ก่อนเพิ่ม handler
      (สำคัญตอน test ที่สร้าง app ใหม่ทุก fixture)
- [ ] ไฟล์ที่ผู้ใช้สร้าง **ไม่เก็บใน `static/`** — เสิร์ฟผ่าน route ที่เช็ค ownership (F05)
- [ ] ใช้ `datetime.now(datetime.UTC)` ไม่ใช่ `datetime.utcnow()` ที่ deprecated แล้ว

## อ้างอิงในสไลด์

- Flask พื้นฐาน / routing / Jinja: **Lecture 4 หน้า 69–101**
- HTTP status code: Lecture 4 หน้า 89–90
- Flask + SQLite CRUD: **Lecture 7 หน้า 99–108**
- Front-End vs Back-End developer: Lecture 4 หน้า 61–62
