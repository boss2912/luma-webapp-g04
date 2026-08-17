# กติกาการทำงานร่วมกัน — LUMA Group 04

---

## Branch

```
main ──────────────────────────────●  release เท่านั้น
                                   ↑ PR
develop ───●───●───●───●───●───●───●  ตรวจงานก่อนเข้า main
           ↑       ↑       ↑
   feat/web-platform  feat/data-layer  feat/ai-ip-engine
       (คนที่ 1)         (คนที่ 2)        (คนที่ 3)
```

| Branch | ใคร | ใช้ทำอะไร |
|---|---|---|
| `main` | – | release เท่านั้น · 🔒 ป้องกันไว้ |
| `develop` | – | รวมงานทุกคน ตรวจก่อนขึ้น main · 🔒 ป้องกันไว้ |
| `feat/web-platform` | คนที่ 1 | backend + frontend + deploy |
| `feat/data-layer` | คนที่ 2 | database |
| `feat/ai-ip-engine` | คนที่ 3 | ai-engine |

### 🔒 `main` และ `develop` push ตรงไม่ได้

repo ตั้ง ruleset ไว้ว่า *"Changes must be made through a pull request"*
ถ้าลอง `git push origin develop` จะได้:
```
remote: error: GH013: Repository rule violations found
remote: - Changes must be made through a pull request.
```
**นี่ไม่ใช่บั๊ก** — ต้องเปิด PR เท่านั้น

### แตก branch ย่อยได้

ถ้างานใหญ่ แตกจาก branch ตัวเองได้:
```bash
git checkout feat/ai-ip-engine
git checkout -b feat/ai-ip-engine/02-enhancement
```
แล้ว PR กลับเข้า branch หลักของตัวเอง หรือเข้า `develop` ตรงก็ได้

---

## Workflow ประจำวัน

```bash
# 1. เริ่มวัน — ดึงงานคนอื่นมาก่อน
git checkout develop
git pull origin develop

# 2. กลับไป branch ตัวเอง แล้วเอา develop เข้ามา
git checkout feat/ai-ip-engine
git merge develop            # แก้ conflict ที่นี่ ไม่ใช่ใน PR

# 3. ทำงาน แล้ว commit
git add -A
git commit -m "feat(pipeline): 02_enhancement histogram equalization"

# 4. push
git push origin feat/ai-ip-engine

# 5. เปิด PR เข้า develop บน GitHub
```

> **ข้อ 2 สำคัญ** — แก้ conflict ใน branch ตัวเองก่อนเปิด PR
> ไม่ใช่เปิด PR แล้วให้คนอื่นเห็น conflict

---

## Commit message

```
<type>(<scope>): <สรุปสั้นๆ>

<รายละเอียด ถ้าจำเป็น>
```

**type**: `feat` · `fix` · `docs` · `test` · `refactor` · `chore`
**scope**: `backend` · `frontend` · `ai` · `pipeline` · `db` · `deploy` · `docs`

ตัวอย่างที่ดี:
```
feat(pipeline): 02_enhancement gamma correction + histogram stats

- power-law transform s = c·r^γ (Lecture 4 หน้า 12-18)
- clamp ค่าเป็น 0-255 แล้ว cast กลับ uint8 กัน overflow
- คืน metrics: mean, variance, skewness, kurtosis
- มีภาพ before/after ใน samples/output/

Closes #7
```

```
fix(backend): validate prompt type before .strip() (F04)
docs(db): schema tags many-to-many แทน comma-string
test(ai): เพิ่ม test IoU ของ selective color mask
```

ตัวอย่างที่ไม่ดี:
```
❌ update
❌ edit_output
❌ fix bug
❌ งานวันนี้
```

---

## Pull Request

### ก่อนเปิด PR — ตรวจ 6 ข้อนี้

- [ ] `pytest` ผ่านทั้งหมด (ไม่ใช่ "ผ่านเกือบหมด")
- [ ] **ไม่มี secret / ไฟล์ `.db` / ไฟล์ `.env` ใน diff** — เช็คด้วย `git diff --stat origin/develop`
- [ ] merge `develop` เข้า branch ตัวเองแล้ว ไม่มี conflict
- [ ] อัปเดต `README.md` ของโฟลเดอร์ที่แก้
- [ ] ถ้าเปลี่ยนสัญญา API → อัปเดต [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md)
- [ ] อ่าน checklist ใน [`archive/SECURITY_FIXES_v1.md`](archive/SECURITY_FIXES_v1.md)

### PR body ควรมี

```markdown
## ทำอะไร
สรุป 2-3 บรรทัด

## อ้างอิงสไลด์
Lecture 4 หน้า 36-42 (Histogram Equalization)

## ทดสอบอย่างไร
- pytest 12/12 ผ่าน
- ทดสอบกับภาพ 5 ภาพใน samples/input/ ผลอยู่ใน samples/output/
- ค่า contrast เพิ่มจาก 0.31 → 0.68

## ที่ยังค้าง
- ยังไม่ทำ histogram specification (แยกเป็น issue อีกอัน)

Closes #7
```

### กติกา review

- **ต้องมีคนอื่น approve อย่างน้อย 1 คน** ก่อน merge
- คนเปิด PR **ไม่ approve PR ตัวเอง**
- review แล้วเจอปัญหา → คอมเมนต์ให้ชัดว่าปัญหาคืออะไร ไม่ใช่แค่ "แก้หน่อย"
- ถ้า reviewer เข้าใจผิด → อธิบายกลับได้ ไม่ต้องแก้ตามทุกอย่าง

### วิธี merge

ใช้ **Merge commit** (`--no-ff`) ไม่ใช่ squash — เพื่อให้เห็นว่าใครทำอะไรเมื่อไหร่
สำคัญสำหรับงานกลุ่มที่ต้องแสดงการมีส่วนร่วม

---

## สิ่งที่ห้ามทำเด็ดขาด

| ห้าม | เพราะ |
|---|---|
| commit ไฟล์ `.db` / `.sqlite` | v1 มี `luma.db` ค้างใน git แล้วทำ test ล้ม 3 ข้อ (schema ไม่ตรง) |
| commit `instance/config.py` หรือ `.env` | v1 เคยหลุด `SECRET_KEY` ขึ้น GitHub — ใครรู้ค่านี้ปลอม session ได้ |
| `git push --force` ไปที่ `main` / `develop` | ทับงานคนอื่น |
| เขียนคอมเมนต์ภาษาไทยใน `requirements.txt` | pip อ่านด้วย codec `cp874` แล้วพังบนเครื่อง locale ไทย |
| แก้โฟลเดอร์ของคนอื่นโดยไม่บอก | conflict + งานทับ |
| hardcode `localhost` หรือ IP ในโค้ด | ระบบต้องรันข้ามเครื่อง (Lecture 4 หน้า 54) |
| เก็บไฟล์ที่ผู้ใช้สร้างใน `static/` | Flask เสิร์ฟให้ทุกคนโดยไม่เช็คสิทธิ์ = IDOR (F05) |
| ทิ้ง PR ค้างเป็นสัปดาห์ | v1 มี 3 PR ค้าง ~900 บรรทัด คนอื่นทำงานบนโค้ดที่มีช่องโหว่ |

---

## เขียน Test

- **ทุกคนเขียน test ของโค้ดตัวเอง** ไม่มีใครเขียนแทนใคร
- test ต้องรันได้โดย**ไม่ต้องมี Stable Diffusion หรือฐานข้อมูลจริง**
  - ai-engine: ใส่ NumPy array เข้าไป เช็ค array ออกมา
  - Forge client: mock HTTP response ด้วย PNG 1×1 base64
  - backend: `config_overrides` + in-memory SQLite

```python
# fixture ที่ใช้ได้เลย (ยกมาจาก v1)
@pytest.fixture()
def app():
    test_app = create_app(config_overrides={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key-not-for-real-use",
        "WTF_CSRF_ENABLED": False,
    })
    yield test_app
    with test_app.app_context():
        db.session.remove()
        db.drop_all()
```

### สิ่งที่ไม่ควรทำในไฟล์ test

v1 มี `test_system_check.py` ที่รันโค้ดตอน **import** แล้วมี test ตัวเดียวมา assert ตัวนับรวมท้ายสุด
ปัญหา: ล้มแล้วบอกแค่ "3 checks failed" ไม่รู้ข้อไหน · `os.chdir()` ตอน import กระทบ test อื่น · ต่อ DB จริง
→ **เขียน test แยกข้อตามปกติ**

---

## เขียนโค้ดอย่างไรให้อ่านง่าย

**คอมเมนต์บอก "ทำไม" ไม่ใช่ "ทำอะไร"**
```python
# ❌ คูณสองแล้วแปลงเป็น int32
hue = hsv[:,:,0].astype(np.int32) * 2

# ✅ OpenCV เก็บ Hue 8-bit ไว้ 0-179 (ไม่ใช่ 0-360) เพราะ 1 ไบต์เก็บได้แค่ 0-255
#    ต้อง astype(int32) ก่อนคูณ ไม่งั้น uint8 ล้น
hue = hsv[:,:,0].astype(np.int32) * 2
```

**อ้างอิงสไลด์ในโค้ดที่มาจากสไลด์**
```python
def gamma_correct(img, gamma, c=1.0):
    """
    Power-law transformation — Lecture 4 หน้า 12-18
        s = c · r^γ
    γ < 1 ทำให้ภาพสว่างขึ้น · γ > 1 ทำให้มืดลง
    """
```
ตอนทำรายงานจะอ้างอิงได้เลยโดยไม่ต้องกลับไปหา

**ในโฟลเดอร์ `pipeline/` ห้าม import Flask** — ให้เป็น pure image processing รับ/คืน NumPy array

---

## เมื่อติดปัญหา

1. อ่าน `README.md` ของโฟลเดอร์นั้นก่อน — มีคำเตือนเรื่องกับดักที่เจอมาแล้ว
2. เช็ค [`archive/ARCHITECTURE_v1.md`](archive/ARCHITECTURE_v1.md) — ปัญหา A–F ที่เคยเจอ
3. เช็คว่า v1 เคยทำเรื่องนี้ไว้ไหม:
   ```bash
   git show backup/v1-final:luma-webapp/app/routes/api.py
   ```
4. ถามในกลุ่ม — บอกด้วยว่าลองอะไรไปแล้ว
