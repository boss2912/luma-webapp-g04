# LUMA v1 — บันทึกช่องโหว่ที่แก้แล้ว (F01–F15)

> ชุด security fix จาก PR #10 (`fix/security-and-issue9`)
> **ทั้งหมดนี้ต้องไม่หลุดกลับมาในโครงใหม่** — ใช้เป็น checklist ตอน review

---

## ตารางสรุป

| รหัส | ช่องโหว่ | ความรุนแรง | ไฟล์ที่แก้ |
|---|---|---|---|
| F01 | Open redirect ผ่าน `?next=` | 🔴 สูง | `routes/auth.py` |
| F02 | `debug=True` + `host="0.0.0.0"` hardcode | 🔴 สูง | `run.py` |
| F03 | `request.form["..."]` โยน `KeyError` → 500 | 🟡 กลาง | `routes/auth.py` |
| F04 | `prompt` ไม่ใช่ string → crash 500 | 🟡 กลาง | `routes/api.py` |
| F05 | **IDOR** — ดูรูปคนอื่นได้โดยไม่ต้องล็อกอิน | 🔴 สูง | `routes/api.py`, `.gitignore` |
| F06 | Flask-WTF ติดตั้งไว้แต่ไม่เคยเปิด `CSRFProtect` | 🔴 สูง | `app/__init__.py` |
| F07 | เช็ค username/email ซ้ำแบบสนตัวพิมพ์เล็กใหญ่ | 🟡 กลาง | `routes/auth.py` |
| F08 | ไม่มี password policy ฝั่ง server | 🟡 กลาง | `routes/auth.py` |
| F09 | `instance/config.py` (มี `SECRET_KEY`) ถูก push ขึ้น git | 🔴 สูง | `.gitignore` |
| F10 | `/api/*` redirect HTML แทนตอบ JSON 401 | 🟢 ต่ำ | `app/__init__.py` |
| F11 | ชื่อไฟล์ชนกันในวินาทีเดียว → ไฟล์เก่าถูกทับ | 🟡 กลาง | `routes/api.py` |
| F12 | Account enumeration จากข้อความ error | 🟡 กลาง | `routes/auth.py` |
| F13 | *(ไม่มีบันทึก — ดูหมายเหตุท้ายเอกสาร)* | – | – |
| F14 | ไม่มี rate limit บน login → brute force ได้ | 🔴 สูง | `routes/auth.py` |
| F15 | Logout เป็น `GET` (มี side effect) | 🟡 กลาง | `routes/auth.py`, `base.html` |
| — | Stored XSS จาก `prompt` ใน gallery | 🔴 สูง | `dashboard.html` |

---

## รายละเอียด

### F01 · Open redirect
**เดิม**: `return redirect(next_page or url_for("main.dashboard"))` — รับ `?next=` มาใช้ตรงๆ
ผู้โจมตีส่งลิงก์ `/auth/login?next=https://evil.example` ให้เหยื่อ พอล็อกอินสำเร็จเว็บก็พาไปเว็บปลอมที่หน้าตาเหมือนกัน (phishing)

**แก้**:
```python
def _is_safe_next_url(target):
    if not target: return False
    parsed = urlparse(target)
    return not parsed.scheme and not parsed.netloc
```
> ต้องเช็ค `netloc` ด้วย ไม่ใช่แค่ `scheme` — `//evil.example` (protocol-relative URL) ไม่มี scheme แต่เบราว์เซอร์ไปเว็บนอกจริง

---

### F02 · Debug mode เปิดให้ทั้ง network
**เดิม**: `app.run(debug=True, host="0.0.0.0", port=5000)` hardcode

Werkzeug debugger **รันโค้ด Python จากหน้าเว็บได้** เมื่อเจอ exception พอ bind `0.0.0.0` = ทุกเครื่องบน LAN ยึดเครื่องได้ ไม่มีรหัสผ่านกั้น

**แก้**: default ปลอดภัยที่สุด + คุมด้วย env var
```python
debug = os.environ.get("LUMA_DEBUG", "0") == "1"
host  = os.environ.get("LUMA_HOST", "127.0.0.1")
```
พร้อมเตือน (ไม่บล็อก) ถ้าตั้งทั้งสองพร้อมกัน

> ⚠️ สำคัญสำหรับโปรเจกต์นี้: สเปกอาจารย์ให้เครื่องคุยกันข้าม LAN จึง **ต้อง** ใช้ `LUMA_HOST=0.0.0.0` ตอน demo — ห้ามเปิด `LUMA_DEBUG` พร้อมกัน

---

### F03 · `KeyError` → 500
**เดิม**: `request.form["email"]` — ถ้า client ส่ง POST มาโดยไม่มีฟิลด์นี้ (curl, bot, ฟอร์มพัง) จะโยน `KeyError` เป็น 500
**แก้**: `request.form.get("email", "")` ทุกที่ + validate เอง → มี regression test ใน `tests/test_auth.py`

---

### F04 · Type confusion บน prompt
**เดิม**: `data.get("prompt", "").strip()` — ส่ง `{"prompt": 12345}` มา → `int.strip()` ไม่มี → 500
**แก้**: เช็ค `isinstance(prompt, str)` ก่อน + `request.get_json(silent=True)` กันกรณี body ไม่ใช่ JSON

> **กับดัก Python ที่ต้องจำ**: `isinstance(True, int)` เป็น `True` — เวลา validate `steps` ต้องเขียน
> `if not isinstance(steps, int) or isinstance(steps, bool)` ไม่งั้น `{"steps": true}` ผ่าน validation

---

### F05 · IDOR (ร้ายแรงที่สุด)
**เดิม**: เก็บรูปที่ `app/static/generated/` แล้วตอบ `image_url: "/static/generated/asset_3_1719...png"`

Flask เสิร์ฟทุกอย่างใน `static/` ให้ **ทุกคน** โดยไม่เช็คอะไรเลย → ไม่ต้องล็อกอิน แค่รู้/เดา URL ก็ดูรูปคนอื่นได้ทั้งหมด

**แก้ 3 ชั้น**:
1. ย้ายที่เก็บออกนอก `static/` → `app/generated/`
2. เพิ่ม `GET /api/assets/<id>/image` ที่ `@login_required` + เช็ค ownership
3. `image_url` ชี้มาที่ endpoint ใหม่

```python
def _get_owned_asset_or_404(asset_id):
    asset = db.session.get(Asset, asset_id)
    if asset is None or asset.user_id != current_user.id:
        abort(404)          # 404 ไม่ใช่ 403 — ไม่บอกว่า id นี้มีจริงหรือเปล่า
    return asset
```

**ผลการทดสอบ**: เจ้าของ → 200 · คนอื่น → 404 · ไม่ล็อกอิน → 401 · id ไม่มีจริง → 404

---

### F06 · CSRF ไม่ถูกเปิดใช้
**เดิม**: `Flask-WTF==1.2.1` อยู่ใน `requirements.txt` แต่ไม่มีใครเรียก `CSRFProtect()` เลย — ติดตั้งไว้เฉยๆ

เว็บอื่นสั่งให้เบราว์เซอร์เหยื่อยิง POST มาที่เว็บนี้แทนผู้ใช้ได้ (เปลี่ยนรหัส, ลบของ) เพราะ cookie session ถูกแนบไปด้วยอัตโนมัติ

**แก้**:
```python
csrf = CSRFProtect()
csrf.init_app(app)
csrf.exempt(api_bp)        # /api/* เป็น JSON ล้วน
```
+ เพิ่ม `{{ csrf_token() }}` ในทุกฟอร์ม HTML

> **บทเรียนสำคัญ**: commit `0cabce5` เปิด CSRF แต่ยังไม่ได้ใส่ `csrf_token()` ในเทมเพลต → ฟอร์มทุกอันพังเงียบๆ ตอบ 400 หมด แก้ตามใน `bc0994c`
> **การเปิด security feature กับการปรับ client ให้รองรับ ต้องอยู่ใน commit เดียวกัน**

---

### F07 + F12 · Duplicate check + Account enumeration
**เดิม**:
```python
if User.query.filter_by(username=username).first():
    flash("ชื่อผู้ใช้นี้ถูกใช้แล้ว")        # ← บอกว่า username นี้มีจริง
if User.query.filter_by(email=email).first():
    flash("อีเมลนี้ถูกใช้แล้ว")            # ← บอกว่า email นี้มีจริง
```

สองปัญหา:
- **F07**: `filter_by` เทียบตรงตัว → สมัคร `Boss` ได้ทั้งที่มี `boss` อยู่แล้ว แล้วชนกันตอนล็อกอิน
- **F12**: แยกข้อความ = ผู้โจมตีวน list อีเมลเพื่อหาว่าใครเป็นสมาชิกได้

**แก้**: เทียบแบบ case-insensitive + รวมเป็นข้อความเดียว
```python
username_taken = User.query.filter(db.func.lower(User.username) == username.lower()).first()
email_taken    = User.query.filter(db.func.lower(User.email) == email).first()
if username_taken or email_taken:
    errors["general"] = "ไม่สามารถสมัครด้วยข้อมูลนี้ได้ / Unable to register with this information"
```

> **สิ่งที่ยังค้าง**: ควรมี `UNIQUE INDEX` แบบ case-insensitive ที่ระดับฐานข้อมูลด้วย — เช็คใน Python มี race condition (สองคนสมัครพร้อมกันด้วย username เดียวกัน) → **งานคนที่ 2 ในโครงใหม่**

---

### F08 · Password policy
**เดิม**: ไม่เช็คความยาวเลย รหัสผ่าน `1` ก็ผ่าน
**แก้**: บังคับ ≥ 8 ตัวฝั่ง server + `minlength="8"` ในฟอร์ม (client-side validate ช่วย UX แต่กันไม่ได้ ต้องมีฝั่ง server ด้วย)

---

### F09 · Secret ถูก push ขึ้น git
**เดิม**: `.gitignore` มีบรรทัด `# instance/config.py` **comment ไว้** → ไฟล์ที่มี `SECRET_KEY` ถูก track และ push ขึ้น GitHub

`SECRET_KEY` ของ Flask ใช้เซ็น session cookie — ใครรู้ค่านี้ปลอม cookie เป็น user คนไหนก็ได้

**แก้**: เอา `config.py` ออกจาก git (`git rm --cached`) + uncomment บรรทัด ignore + สร้าง key ใหม่ในเครื่อง + เหลือแค่ `config.py.example`

> `create_app()` ต้องใส่ `silent=True` ด้วย เพราะไฟล์นี้ไม่มีในเครื่องที่เพิ่ง clone

---

### F10 · JSON endpoint redirect เป็น HTML
**แก้**: `@login_manager.unauthorized_handler` เช็ค `request.path.startswith("/api/")` แล้วตอบ JSON 401

---

### F11 · ชื่อไฟล์ชนกัน
**เดิม**: `f"asset_{user.id}_{int(time.time())}.png"` — ความละเอียดระดับวินาที generate 2 ครั้งในวินาทีเดียวกัน ไฟล์แรกถูกทับ (แถว DB ยังอยู่ แต่ชี้ไปไฟล์ที่เนื้อหาเปลี่ยนแล้ว)
**แก้**: `uuid.uuid4().hex[:12]`

---

### F14 · Brute force
**แก้**: in-memory rate limiter 5 ครั้ง / 60 วินาที → 429

**จุดที่ปรับตอน review (f78a395)**: เดิม key ด้วย `request.remote_addr` — คนที่ใช้ network เดียวกัน (network มหาลัย/ออฟฟิศ ที่ NAT ออกไป IP เดียว) จะถูกล็อกไปด้วยทั้งที่ไม่เกี่ยว เปลี่ยนไป key ด้วย **email ที่พยายามล็อกอิน** จำกัดผลกระทบไว้แค่ account เป้าหมาย

> ⚠️ เก็บใน memory ของ process เดียว — V5 ที่มีหลาย worker ต้องย้ายไป Redis

---

### F15 · Logout ผ่าน GET
**เดิม**: `@auth_bp.route("/logout")` (GET) + `<a href="...">Logout</a>`

GET ไม่ควรมี side effect — link prefetch ของเบราว์เซอร์, crawler, หรือ `<img src="/auth/logout">` ที่ฝังในเว็บอื่นทำให้ผู้ใช้ถูก logout โดยไม่ตั้งใจ

**แก้**: `methods=["POST"]` + เปลี่ยน nav เป็น `<form method="POST">` พร้อม `csrf_token()`

**บั๊ก CSS ที่ตามมา** (แก้ใน `f78a395`): `.nav-link-btn` (specificity 0,1,0) แพ้ `button[type="submit"]` (0,1,1) ที่มีอยู่ก่อน → ปุ่ม Logout เลยขึ้นเป็นปุ่มทึบแทนลิงก์ธรรมดา แก้โดย qualify selector เป็น `.nav-logout-form .nav-link-btn`
> **บทเรียน**: เปลี่ยน `<a>` เป็น `<button>` ต้องคิดเรื่อง CSS specificity ที่มีอยู่เดิมด้วย

---

### เพิ่มเติม · Stored XSS ใน gallery
**เดิม**: dashboard เอาผลลัพธ์มาแสดงด้วย `JSON.stringify(data)` ตรงๆ พอทำ gallery จริงต้องแสดง `prompt` ที่ผู้ใช้พิมพ์เอง

ถ้าใช้ `innerHTML` แล้วมีคนตั้ง prompt เป็น `<script>fetch('/api/assets').then(...)</script>` โค้ดจะรันในเบราว์เซอร์ของทุกคนที่เห็น asset นั้น

**แก้**: ใช้ `textContent` ไม่ใช่ `innerHTML` สำหรับข้อความจากผู้ใช้

**บั๊ก CSS ที่เจอตอนนั้น**: `[hidden]` ถูก override ได้ด้วยกฎที่มาทีหลัง (เช่น `.spinner { display: inline-block }`) → spinner โชว์ทั้งที่ควรซ่อน แก้ด้วย
```css
[hidden] { display: none !important; }
```

---

## หมายเหตุเรื่อง F13

ไม่พบร่องรอย F13 ทั้งในโค้ด คอมเมนต์ และ commit message — ลำดับที่มีบันทึกจริงคือ F01–F12, F14, F15
เป็นไปได้ว่าเป็นข้อที่ตรวจแล้วไม่ใช่ปัญหาจริง หรือถูกรวมกับข้ออื่น **ไม่ใช่ช่องโหว่ที่ค้างอยู่**

---

## Checklist สำหรับโครงใหม่

คัดลอกไปใช้ตอน review PR:

- [ ] `?next=` / redirect ทุกจุด validate ว่าเป็น relative path (F01)
- [ ] `debug` / `host` มาจาก env var ไม่ hardcode (F02)
- [ ] อ่าน `request.form` / `request.get_json` ด้วย `.get()` + `silent=True` (F03, F04)
- [ ] validate ชนิดข้อมูลก่อนเรียก method ของมัน + ระวัง `bool` เป็น `int` (F04)
- [ ] ไฟล์ที่ผู้ใช้อัปโหลด/สร้าง **ไม่อยู่ใน `static/`** ต้องผ่าน route ที่เช็ค ownership (F05)
- [ ] `CSRFProtect` เปิดใช้จริง + ทุกฟอร์มมี `csrf_token()` **ใน commit เดียวกัน** (F06)
- [ ] เทียบ username/email แบบ case-insensitive + `UNIQUE INDEX` ที่ DB (F07)
- [ ] password policy ฝั่ง server (F08)
- [ ] ไม่มี secret ใดๆ ใน git — เหลือแค่ `.example` (F09)
- [ ] `/api/*` ตอบ JSON ทุกกรณีรวม error (F10)
- [ ] ชื่อไฟล์ใช้ uuid ไม่ใช่ timestamp (F11)
- [ ] ข้อความ error ไม่บอกว่า account มีอยู่จริงหรือเปล่า (F12)
- [ ] rate limit บน endpoint ที่ยืนยันตัวตน (F14)
- [ ] action ที่มี side effect เป็น POST/DELETE ไม่ใช่ GET (F15)
- [ ] ข้อความจากผู้ใช้แสดงด้วย `textContent` / Jinja auto-escape ไม่ใช่ `innerHTML` / `|safe`
- [ ] ไม่ commit ไฟล์ `.db`
