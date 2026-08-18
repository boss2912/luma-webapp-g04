# ทีมจริงเขาทำกันอย่างไร — สำรวจจากโปรเจกต์จริงบน GitHub

> เอกสารนี้ตอบคำถามสองข้อ
>
> 1. **โปรเจกต์ที่คล้าย LUMA เขาวางโครงสร้างโฟลเดอร์กันแบบไหน**
> 2. **ในความเป็นจริง คนหลายคนทำงานบนโปรเจกต์เดียวกันได้อย่างไร โดยไม่ตีกัน**
>
> ข้อ 2 คือข้อที่สำคัญกว่า เพราะโครงสร้างโฟลเดอร์เป็นแค่ผลลัพธ์
> ของการแก้ปัญหา "คนหลายคนแตะโค้ดชุดเดียวกัน" เท่านั้น

**สำรวจเมื่อ**: 18 ส.ค. 2026 · ข้อมูลดาวและโครงสร้างดึงจาก GitHub API ตรงในวันนั้น

---

## สารบัญ

- [วิธีหาข้อมูล](#วิธีหาข้อมูล)
- [ส่วนที่ 1 — โครงสร้างโฟลเดอร์](#ส่วนที่-1--โครงสร้างโฟลเดอร์)
  - [ตารางเทียบ 5 โปรเจกต์จริง](#ตารางเทียบ-5-โปรเจกต์จริง)
  - [กฎ 6 ข้อที่ทุกโปรเจกต์ทำเหมือนกัน](#กฎ-6-ข้อที่ทุกโปรเจกต์ทำเหมือนกัน)
  - [ชั้นในของ service — จุดที่ LUMA ยังขาด](#ชั้นในของ-service--จุดที่-luma-ยังขาด)
  - [LUMA อยู่ตรงไหนเมื่อเทียบกับเขา](#luma-อยู่ตรงไหนเมื่อเทียบกับเขา)
- [ส่วนที่ 2 — คนหลายคนทำงานร่วมกันได้อย่างไร](#ส่วนที่-2--คนหลายคนทำงานร่วมกันได้อย่างไร)
  - [ปัญหา 6 ข้อที่เกิดเสมอ](#ปัญหา-6-ข้อที่เกิดเสมอ)
  - [กลไกที่ 1 — CODEOWNERS](#กลไกที่-1--codeowners-ใครเป็นเจ้าของโฟลเดอร์ไหน)
  - [กลไกที่ 2 — แตกกิ่งแบบไหน](#กลไกที่-2--แตกกิ่งแบบไหน)
  - [กลไกที่ 3 — PR ต้องเล็ก](#กลไกที่-3--pr-ต้องเล็ก-มีตัวเลขวิจัยรองรับ)
  - [กลไกที่ 4 — สัญญาก่อนโค้ด](#กลไกที่-4--สัญญาก่อนโค้ด-contract-first)
  - [กลไกที่ 5 — CI เป็นกรรมการ](#กลไกที่-5--ci-เป็นกรรมการที่ไม่มีใครเถียง)
  - [กลไกที่ 6 — template และ label](#กลไกที่-6--template-และ-label)
  - [กลไกที่ 7 — บันทึกการตัดสินใจ](#กลไกที่-7--บันทึกการตัดสินใจ)
- [ส่วนที่ 3 — หนึ่งสัปดาห์ของทีมจริง](#ส่วนที่-3--หนึ่งสัปดาห์ของทีมจริงหน้าตาเป็นอย่างไร)
- [ส่วนที่ 4 — ช่องว่างของ LUMA](#ส่วนที่-4--ช่องว่างของ-luma-และควรอุดข้อไหน)
- [แหล่งอ้างอิง](#แหล่งอ้างอิง)

---

## วิธีหาข้อมูล

ไม่ได้อ่านแค่บทความ "best practice" เพราะบทความมักเขียนจากอุดมคติ
จึงดึง **โครงสร้างจริงของ repo จริง** ผ่าน GitHub API มาเทียบกัน แล้วดูว่าอะไรที่ทุกคนทำเหมือนกัน

เกณฑ์เลือกโปรเจกต์: ต้องเป็นระบบที่ **มีหลายส่วนประกอบเหมือน LUMA** คือมีหน้าเว็บ
มี backend มีส่วนประมวลผลภาพ/AI และมีฐานข้อมูล — ไม่ใช่ไลบรารีเดี่ยวๆ

---

## ส่วนที่ 1 — โครงสร้างโฟลเดอร์

### ตารางเทียบ 5 โปรเจกต์จริง

| โปรเจกต์ | ดาว | ภาษา | ทำอะไร | โครงระดับบนสุด |
|---|---:|---|---|---|
| [immich](https://github.com/immich-app/immich) | 111k | TypeScript | คลังรูปภาพ self-hosted + AI จำแนกภาพ | `server/` `web/` `machine-learning/` `mobile/` `e2e/` `docs/` `deployment/` `docker/` |
| [stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) | 164k | Python | ต้นทางของ Forge ที่เราใช้ | `modules/` `extensions/` `extensions-builtin/` `javascript/` `models/` `configs/` `test/` |
| [photoprism](https://github.com/photoprism/photoprism) | 40k | Go | จัดการรูปภาพ + AI ติดป้ายอัตโนมัติ | `internal/` `pkg/` `frontend/` `cmd/` `assets/` `setup/` `docker/` |
| [InvokeAI](https://github.com/invoke-ai/InvokeAI) | 28k | Python | สร้างภาพด้วย Stable Diffusion | `invokeai/` `tests/` `docs/` `docker/` `scripts/` |
| [IOPaint](https://github.com/Sanster/IOPaint) | 23k | Python | ลบวัตถุออกจากภาพ (inpainting) | `iopaint/` `web_app/` `docker/` `scripts/` `assets/` |

**immich คือตัวที่ตรงกับ LUMA ที่สุด** — แยก `server` / `web` / `machine-learning`
ซึ่งเป็นแนวคิดเดียวกับ `services/backend` / `services/frontend` / `services/ai-engine` ของเรา
และเขาก็ deploy แยกเครื่องกันจริงเหมือนที่อาจารย์ให้ทำ

### กฎ 6 ข้อที่ทุกโปรเจกต์ทำเหมือนกัน

**1. แบ่งชั้นบนสุดตาม "สิ่งที่ deploy แยกกัน" ไม่ใช่ตามชนิดไฟล์**

ไม่มีโปรเจกต์ไหนแบ่งเป็น `python/` `html/` `css/` เลย
เพราะขอบเขตที่มีความหมายจริงคือ **ขอบเขตที่ deploy แยกกันได้**

> ตรงนี้สำคัญกับ LUMA เป็นพิเศษ เพราะอาจารย์กำหนดให้แยก 3 เครื่องอยู่แล้ว
> (Lecture 4 หน้า 54, 56) โครง `services/` ของเราจึงตรงกับเหตุผลนี้พอดี

**2. แต่ละ service มีไฟล์ dependency ของตัวเอง**

- immich: `server/package.json` และ `machine-learning/pyproject.toml` แยกกันคนละไฟล์
- IOPaint: `requirements.txt` + `requirements-dev.txt` แยกกัน

ยืนยันว่าการที่ LUMA แยก `requirements.txt` 3 ไฟล์ **ไม่ใช่การทำให้ซับซ้อนเกินจำเป็น**
แต่เป็นสิ่งที่ทีมจริงทำ เพราะเครื่อง backend ไม่ควรต้องลง OpenCV
(ดู [`DECISIONS.md` ADR-001](DECISIONS.md#adr-001--package-ที่ใช้ร่วมกันต้องล็อกเวอร์ชันตรงกันทุก-service))

**3. แต่ละ service มี test ของตัวเอง อยู่ติดกับโค้ดที่มันทดสอบ**

`server/test/` · `machine-learning/test_main.py` · `iopaint/tests/`
ไม่ใช่กอง `tests/` ใหญ่ที่รูท

**4. `docs/` แยกจากโค้ดเสมอ**

ทุกโปรเจกต์มี `docs/` เป็นโฟลเดอร์ระดับบนสุด

**5. เรื่อง deploy อยู่คนละที่กับโค้ด**

`docker/` `deployment/` `setup/` `compose.yaml` — แยกออกจาก logic เสมอ
LUMA ใช้ `deploy/` ทำหน้าที่เดียวกัน

**6. มีไฟล์ "ประตูหน้าบ้าน" ครบชุดที่รูท**

`README.md` · `CONTRIBUTING.md` · `LICENSE` · `.gitignore` · `CODEOWNERS` · `SECURITY.md`

photoprism มีไฟล์ที่น่าสนใจเพิ่มคือ **`CODEMAP.md`** และ **`GLOSSARY.md`**
— แผนที่บอกว่าโค้ดส่วนไหนอยู่ไหน และอภิธานศัพท์ของโปรเจกต์
สองไฟล์นี้มีไว้เพื่อ **ลดเวลาที่คนใหม่ต้องใช้กว่าจะแก้โค้ดบรรทัดแรกได้**

### ชั้นในของ service — จุดที่ LUMA ยังขาด

ดูข้างใน `immich/server/src/` จะเห็นการแบ่งชั้นที่ชัดมาก:

```text
server/src/
├── controllers/     รับ HTTP request  ตรวจ input  แล้วส่งต่อ   <- บางที่สุด
├── services/        ตรรกะธุรกิจทั้งหมด                        <- หนาที่สุด
├── repositories/    คุยกับฐานข้อมูล / ไฟล์ / service ภายนอก
├── dtos/            รูปร่างของ request และ response
├── schema/          โครงตาราง
├── queries/         SQL ที่ซับซ้อน
├── middleware/      auth, logging, rate limit
├── workers/         งานเบื้องหลัง (คิว)
└── utils/
```

หัวใจคือ **controller → service → repository** และกฎว่า
"ห้าม controller คุยกับฐานข้อมูลตรงๆ" — ใน PR template ของ immich มีข้อนี้เป็น checklist
ให้ผู้เขียนติ๊กเองเลยว่า *"โค้ดใน `src/services/` ใช้ repository ในการแตะฐานข้อมูล"*

**เทียบกับ LUMA**

| ชั้น | immich | LUMA (v2) | สถานะ |
|---|---|---|---|
| รับ request | `controllers/` | `app/routes/` | ✅ มี |
| ตรรกะธุรกิจ | `services/` | `app/services/` | ✅ มี |
| แตะฐานข้อมูล | `repositories/` | — (routes เรียก model ตรงๆ) | ⚠️ **ยังไม่มี** |
| รูปร่าง request/response | `dtos/` | `docs/API_CONTRACT.md` (เอกสาร ไม่ใช่โค้ด) | ⚠️ เป็นเอกสาร |
| ตาราง | `schema/` | `app/models/` + `services/database/schema/` | ✅ มี |
| งานเบื้องหลัง | `workers/` | `services/ai-engine/queue/` | ✅ วางที่ไว้แล้ว |

**ควรเพิ่ม `repositories/` ไหม?** — สำหรับทีม 3 คนกับ endpoint ไม่กี่ตัว **ยังไม่ต้อง**
มันจะกลายเป็นการเขียนโค้ดผ่านชั้นเปล่าๆ โดยไม่ได้ประโยชน์

แต่ควรรับ **กฎ** มาใช้: `routes/` ห้ามเขียน query เอง ให้เรียกผ่าน `services/`
กฎนี้ได้ประโยชน์ 90% ของการแยกชั้น โดยไม่ต้องเพิ่มโฟลเดอร์เลย

### LUMA อยู่ตรงไหนเมื่อเทียบกับเขา

| กฎ | LUMA ทำแล้ว |
|---|---|
| แบ่งตามสิ่งที่ deploy แยก | ✅ `services/{backend,frontend,ai-engine,database}` |
| dependency แยกต่อ service | ✅ 3 ไฟล์ + `requirements-dev.txt` |
| test อยู่ติดโค้ด | ✅ `services/*/tests/` |
| `docs/` แยก | ✅ |
| deploy แยก | ✅ `deploy/` |
| ไฟล์ประตูหน้าบ้าน | ✅ README / CONTRIBUTING / .gitignore · ⚠️ ยังไม่มี CODEOWNERS |

สรุป: **โครงสร้างของ LUMA ตรงกับที่ทีมจริงใช้แล้ว** ไม่ต้องรื้ออะไร
สิ่งที่ยังขาดไม่ใช่โฟลเดอร์ แต่เป็น **กลไกการทำงานร่วมกัน** ซึ่งคือส่วนที่ 2

---

## ส่วนที่ 2 — คนหลายคนทำงานร่วมกันได้อย่างไร

### ปัญหา 6 ข้อที่เกิดเสมอ

นี่คือสิ่งที่เกิดจริงเมื่อคนมากกว่าหนึ่งคนแตะโปรเจกต์เดียวกัน:

| # | ปัญหา | หน้าตาตอนเกิดจริง |
|---|---|---|
| 1 | **แก้ไฟล์เดียวกันพร้อมกัน** | merge conflict ที่ใช้เวลาแก้นานกว่าตอนเขียนโค้ด |
| 2 | **รอกันเป็นลูกโซ่** | "ผมทำต่อไม่ได้ ต้องรอ API ของคุณเสร็จก่อน" |
| 3 | **เข้าใจสัญญาไม่ตรงกัน** | ฝั่งหนึ่งส่ง `tags` เป็น array อีกฝั่งรอ string |
| 4 | **ใครแก้อะไรไม่มีใครรู้** | โค้ดที่ทำงานอยู่ดีๆ พังโดยไม่มีใครรู้ว่าเพราะ commit ไหน |
| 5 | **มาตรฐานไม่เท่ากัน** | คนหนึ่งเขียน test คนหนึ่งไม่เขียน แล้วเถียงกันว่าอันไหนถูก |
| 6 | **คนหนึ่งรู้เรื่องเดียว** | คนนั้นไม่ว่าง = ทั้งทีมหยุด (bus factor = 1) |

ทุกกลไกด้านล่างมีไว้แก้ข้อใดข้อหนึ่งในนี้ **ไม่มีอันไหนเป็นพิธีกรรมเปล่าๆ**

### กลไกที่ 1 — CODEOWNERS: ใครเป็นเจ้าของโฟลเดอร์ไหน

นี่คือคำตอบตรงที่สุดของคำถาม "ทำงานกันหลายคนได้ยังไง"

ไฟล์ `CODEOWNERS` จริงของ immich (ดึงมาเมื่อ 18 ส.ค. 2026):

```text
/.github/           @bo0tzz
/docker/            @bo0tzz
/server/            @danieldietzler
/web/               @danieldietzler
/machine-learning/  @mertalev
/e2e/               @danieldietzler
/mobile/            @shenlong-tanwen @santoshakil @agg23
```

โปรเจกต์ 111,000 ดาว ที่มีคนส่ง PR เข้ามาจากทั่วโลก บริหารด้วยกฎง่ายๆ แค่นี้:
**หนึ่งโฟลเดอร์ มีเจ้าของชัดเจน**

GitHub จะ **ดึงเจ้าของมาเป็นผู้รีวิวอัตโนมัติ** เมื่อ PR แตะโฟลเดอร์นั้น
ไม่มีใครต้องถามว่า "อันนี้ให้ใครดู"

**สังเกตว่ามันตรงกับการแบ่งงาน 3 คนของ LUMA พอดี** ซึ่งไม่ใช่ความบังเอิญ —
โครงสร้างโฟลเดอร์ที่ดีคือโครงสร้างที่แบ่งงานให้คนได้โดยไม่ต้องทับกัน

ไฟล์ที่ LUMA ควรมี (ใช้ชื่อ GitHub ของแต่ละคน):

```text
# .github/CODEOWNERS
/services/frontend/    @<คนที่1>
/services/backend/     @<คนที่1>
/services/database/    @<คนที่2>
/services/ai-engine/   @<คนที่3>
/docs/API_CONTRACT.md  @<คนที่1> @<คนที่2> @<คนที่3>   # สัญญาร่วม ต้องเห็นชอบทุกคน
/docs/DECISIONS.md     @<คนที่1> @<คนที่2> @<คนที่3>
```

บรรทัดสองบรรทัดสุดท้ายคือหัวใจ: **ไฟล์ที่เป็นข้อตกลงร่วม ต้องให้ทุกคนอนุมัติ**
เพราะการแก้สัญญาฝ่ายเดียวคือต้นเหตุของปัญหาข้อ 3

### กลไกที่ 2 — แตกกิ่งแบบไหน

มีสามแบบหลักที่ใช้กันจริง:

| แบบ | หน้าตา | เหมาะกับ |
|---|---|---|
| **Git Flow** | `main` + `develop` + `feature/*` + `release/*` + `hotfix/*` | ซอฟต์แวร์ที่ปล่อยเป็นเวอร์ชัน มีหลายเวอร์ชันต้องดูแลพร้อมกัน |
| **GitHub Flow** | `main` + `feature/*` แล้ว merge กลับเลย | เว็บที่ deploy บ่อย |
| **Trunk-Based** | ทุกคนลง `main` วันละครั้งอย่างน้อย กิ่งอายุสั้นมาก | ทีมที่มี CI แข็งแรง |

**ฉันทามติปี 2026 คือ trunk-based เหมาะกับทีมเล็กที่สุด** เหตุผลไม่ใช่เพราะทันสมัยกว่า
แต่เพราะ **Git Flow เพิ่มภาระให้ทีมเล็กโดยไม่ได้ประโยชน์ตอบแทน**
โปรเจกต์นักศึกษาไม่ต้องดูแลเวอร์ชันเก่าให้ลูกค้า จึงไม่ต้องมี `release/*` และ `hotfix/*`

หลักการที่ **สำคัญกว่าชื่อรูปแบบ** คือ:

> **กิ่งยิ่งอยู่นาน ยิ่งเจ็บตอน merge**
>
> กิ่งที่แยกไป 2 สัปดาห์ = `main` เดินหน้าไป 2 สัปดาห์ = conflict มหาศาล
> นี่คือสาเหตุอันดับหนึ่งของปัญหาข้อ 1

**LUMA ใช้แบบไหน**

ตอนนี้เป็น Git Flow แบบย่อ: `main` ← `develop` ← `feat/*` (3 กิ่งงาน)
ซึ่ง **เหมาะกับสถานการณ์นี้** เพราะอาจารย์ตรวจเป็นเวอร์ชัน V1–V5 (Lecture 4 หน้า 103)
`main` จึงควรเป็นสิ่งที่สาธิตได้เสมอ ส่วน `develop` เป็นที่รวมงาน

แต่ต้องรับกฎของ trunk-based มาใช้ด้วย:

> **`feat/*` ทั้งสามกิ่งต้อง `git merge develop` เข้ามาอย่างน้อยสัปดาห์ละครั้ง**
> ไม่ใช่ปล่อยยาว 3 สัปดาห์แล้วค่อยมาชนกันตอนใกล้ส่ง

### กลไกที่ 3 — PR ต้องเล็ก (มีตัวเลขวิจัยรองรับ)

นี่เป็นเรื่องที่มีข้อมูลชัดเจน ไม่ใช่ความเห็น:

| ขนาด PR | สิ่งที่เกิดขึ้น |
|---|---|
| < 200 บรรทัด | ได้รับอนุมัติ **เร็วกว่า 3 เท่า** · เจอ bug ต่อบรรทัดสูงสุด |
| 200–400 บรรทัด | จุดที่วิจัยชี้ว่าดีที่สุด — เจอ bug **70–90%** ในเวลา 60–90 นาที |
| > 400 บรรทัด | ทีมที่คุม PR ไม่เกิน 400 บรรทัด มี bug ขึ้น production **น้อยลง 40%** |
| > 1,000 บรรทัด | อัตราการเจอ bug **ต่ำลง 70%** — ใหญ่เกินกว่าจะรีวิวได้จริง |

การศึกษาของทีม Cisco พบว่ารีวิว 200–400 บรรทัดใน 60–90 นาที เจอข้อบกพร่อง 70–90%
และหลังผ่าน 60–90 นาที **อัตราการเจอ bug เริ่มตกลง** เพราะสมาธิคนหมด

**ความหมายจริง**: PR 1,000 บรรทัดไม่ได้แปลว่า "รีวิวนานหน่อย" แต่แปลว่า
**"อนุมัติผ่านโดยแทบไม่ได้ตรวจ"** — คนกดผ่านเพราะเหนื่อย ไม่ใช่เพราะมั่นใจ

> สำหรับ LUMA: **1 issue = 1 PR** และถ้า issue ไหนใหญ่จนเกิน 400 บรรทัด ให้ซอยเป็นสอง issue
> issue #14–#33 ที่เปิดไว้ซอยมาในระดับนี้อยู่แล้ว

### กลไกที่ 4 — สัญญาก่อนโค้ด (contract-first)

นี่คือคำตอบของปัญหาข้อ 2 และ 3 และเป็นสิ่งที่หลายทีมนักศึกษาพลาด

**วิธีที่ผิด (ทำตามลำดับ)**

```text
คนที่ 2 ทำฐานข้อมูลเสร็จ -> คนที่ 1 ค่อยเขียน API -> คนที่ 3 ค่อยต่อ AI
```

ผลคือ **มีคนทำงานได้ทีละคน** อีกสองคนนั่งรอ แล้วสามสัปดาห์สุดท้ายทุกคนแย่งกันทำพร้อมกัน

**วิธีที่ถูก (ตกลงสัญญาก่อน แล้วแยกกันทำพร้อมกัน)**

```text
ทุกคนนั่งลงตกลง API_CONTRACT.md ด้วยกัน   <- ใช้เวลาไม่กี่ชั่วโมง
        |
   +----+----+----------+
   |         |          |
คนที่ 1   คนที่ 2    คนที่ 3        <- ทำพร้อมกันได้ทันที
เขียน API  ทำ schema  ทำ pipeline
ยิงใส่ mock  ใส่ข้อมูล  ทดสอบแยก
```

immich ทำเรื่องนี้จริงจังถึงขั้นมี CI ชื่อ **`check-openapi.yml`** คอยตรวจว่า
สัญญา API ที่ generate จากโค้ดยังตรงกับไฟล์สัญญาที่ commit ไว้ — ถ้าไม่ตรง CI แดงทันที
เขามีโฟลเดอร์ `open-api/` แยกไว้ต่างหากเลย

**LUMA ทำเรื่องนี้ไปแล้ว** ผ่านสองอย่าง:

1. `docs/API_CONTRACT.md` — สัญญาที่เขียนไว้ก่อนมีโค้ด และมีตาราง
   "จุดที่ต้องตกลงกันก่อนเขียนโค้ด" 7 ข้อรออยู่
2. `tools/mock_forge_server.py` — **Forge ปลอม** ที่พูดภาษาเดียวกับของจริง
   ทำให้คนที่ 1 ทดสอบ `POST /api/generate` ได้ทันที **โดยไม่ต้องรอคนที่ 3
   และไม่ต้องมีการ์ดจอ** (ดู [ADR-005](DECISIONS.md#adr-005--ทดสอบ-backend-ด้วย-forge-ปลอม-ไม่ผูกกับเครื่อง-gpu))

> mock ไม่ได้มีไว้ขี้เกียจ — มันคือสิ่งที่ทำให้ **คนสามคนทำงานพร้อมกันได้จริง**
> แทนที่จะต่อคิวกัน

### กลไกที่ 5 — CI เป็นกรรมการที่ไม่มีใครเถียง

immich มี workflow **23 ไฟล์** ใน `.github/workflows/` ที่น่าสนใจคือ:

| workflow | ทำอะไร | แก้ปัญหาข้อ |
|---|---|---|
| `test.yml` | รัน test ทุก PR | 4 |
| `static_analysis.yml` | ตรวจสไตล์โค้ด | 5 |
| `check-openapi.yml` | เช็คว่าสัญญา API ยังตรง | 3 |
| `org-pr-require-conventional-commit.yml` | บังคับรูปแบบ commit message | 5 |
| `pr-labeler.yml` | ติด label ให้ PR อัตโนมัติตามโฟลเดอร์ที่แตะ | 4 |
| `codeql-analysis.yml` | สแกนช่องโหว่ความปลอดภัย | — |

**เหตุผลที่ลึกกว่าเรื่องเทคนิค**: CI ทำให้ *"เขียน test ด้วยสิ"* เปลี่ยนจาก
**การว่ากล่าวกันเอง** เป็น **กติกาของระบบ** เพื่อนไม่ต้องเป็นคนบอกเพื่อนว่าทำไม่ครบ
เครื่องบอกให้ — เรื่องนี้สำคัญกับทีมนักศึกษาที่เป็นเพื่อนกันมาก
เพราะไม่มีใครอยากเป็นคนจู้จี้

**LUMA ทำแบบนี้แล้วในเครื่อง** ผ่าน `tools/check_all.py` + pre-commit hook
ซึ่งได้ผลเหมือนกันโดยไม่ต้องตั้ง GitHub Actions:

```bash
python tools/check_all.py --install-hook   # ทำครั้งเดียวต่อเครื่อง
```

> ข้อควรรู้: `.git/hooks/` **ไม่ขึ้น git** ทุกคนต้องรันคำสั่งนี้เองคนละครั้ง
> ถ้าอยากบังคับจริงๆ ต้องย้ายไป GitHub Actions

### กลไกที่ 6 — template และ label

**PR template** — immich ให้ผู้เขียน PR ติ๊ก checklist เอง มีข้อที่น่าเอาอย่าง:

- อ่าน `CONTRIBUTING.md` แล้ว
- **รีวิวโค้ดตัวเองก่อนแล้ว**
- แก้เอกสารที่เกี่ยวข้องแล้ว
- **ไม่มีการแก้ที่ไม่เกี่ยวข้องปนมาใน PR นี้**
- ยืนยันว่า dependency ที่เพิ่มมาจำเป็นจริง
- เขียน test ให้โค้ดใหม่แล้ว
- ตามแบบแผนการตั้งชื่อของโค้ดรอบข้าง

สองข้อที่มีค่าที่สุดคือ **"รีวิวตัวเองก่อน"** (จับ bug ง่ายๆ ได้ก่อนเสียเวลาคนอื่น)
และ **"ไม่มีการแก้ที่ไม่เกี่ยวข้องปน"** (ทำให้ PR เล็กตามกลไกที่ 3)

> เกร็ด: immich เพิ่มช่องใหม่ในปี 2026 ให้ระบุว่า **ใช้ AI ช่วยเขียน PR นี้มากน้อยแค่ไหน**
> สะท้อนว่าวงการกำลังปรับตัวเรื่องนี้อยู่

**Label อัตโนมัติ** — `.github/labeler.yml` ผูก path เข้ากับ label:

```yaml
🖥️web:
  - changed-files:
      - any-glob-to-any-file:
          - web/src/**
```

PR ที่แตะ `web/src/` จะได้ label `🖥️web` เอง ทำให้เห็นภาพรวมได้ทันทีว่าใครทำอะไรอยู่

### กลไกที่ 7 — บันทึกการตัดสินใจ

ปัญหาข้อ 6 (คนหนึ่งรู้เรื่องเดียว) แก้ด้วยการ **เขียนเหตุผลลงไฟล์**

InvokeAI และ photoprism มีไฟล์ `AGENTS.md` ที่รูท photoprism มี `CODEMAP.md` + `GLOSSARY.md`
ทั้งหมดคือความพยายามเดียวกัน: **เอาความรู้ที่อยู่ในหัวคน ออกมาไว้ในที่ที่ทุกคนอ่านได้**

LUMA ใช้ [`docs/DECISIONS.md`](DECISIONS.md) ทำหน้าที่นี้ (รูปแบบ ADR)
เพราะโค้ดบอกได้แค่ว่าทำอะไร แต่บอกไม่ได้ว่า **ทำไมไม่ทำอีกแบบ**

---

## ส่วนที่ 3 — หนึ่งสัปดาห์ของทีมจริงหน้าตาเป็นอย่างไร

ถอดออกมาเป็นรูปธรรมสำหรับทีม 3 คน:

**ต้นสัปดาห์ (15–30 นาที)**

- เปิด GitHub Issues ดูด้วยกัน แต่ละคนหยิบ issue ของตัวเอง **ไม่เกิน 2 อัน**
  (คนที่หยิบ 5 อันพร้อมกัน = ไม่เสร็จสักอัน แล้วไม่มีใครกล้าไปแตะเพราะเป็นของเขา)
- พูดออกมาว่าสัปดาห์นี้จะแตะไฟล์ไหนบ้าง — ประโยคเดียวสั้นๆ
  *"อาทิตย์นี้ผมจะรื้อ auth นะ"* ป้องกันปัญหาข้อ 1 ได้มากกว่าเครื่องมือใดๆ
- ถ้ามีอะไรกระทบ `API_CONTRACT.md` **ต้องคุยตอนนี้ ไม่ใช่ตอนเขียนโค้ดไปแล้วครึ่งทาง**

**ระหว่างสัปดาห์**

- ทำงานบนกิ่งของตัวเอง commit ย่อยๆ บ่อยๆ
- **ดึง `develop` เข้ากิ่งตัวเองอย่างน้อยสัปดาห์ละครั้ง**
- ติดตรงไหนเกิน 30 นาที → ถาม อย่านั่งงมเอง (นี่คือข้อที่คนมักทำผิดที่สุด)

**ตอนจะส่งงาน**

```bash
python tools/check_all.py --with-tests     # ต้องเขียวก่อน
```

เปิด PR → ใส่คำอธิบายว่า **ทำไม** ไม่ใช่แค่ว่าทำอะไร (ว่าทำอะไร ดู diff เอาได้)

**ตอนรีวิว**

- รีวิวภายใน 1 วัน — PR ที่ค้าง 3 วันจะ conflict จนต้องเขียนใหม่
- **แยกให้ออกระหว่าง "ผิด" กับ "ฉันจะเขียนอีกแบบ"** — อย่างหลังพูดได้แต่ไม่ควรบล็อก PR
- ชมด้วยเมื่อเจอโค้ดที่ดี รีวิวที่มีแต่คำติทำให้คนกลัวการส่ง PR

**ปลายสัปดาห์**

- merge เข้า `develop` แล้วตรวจว่ายังรันได้
- ถ้าถึงหมุด V1–V5 ก็ merge `develop` → `main` แล้วติด tag

**สิ่งที่ทีมจริงทำแล้วทีมนักศึกษามักไม่ทำ**

| สิ่งที่ควรทำ | ทำไม |
|---|---|
| เขียนสิ่งที่ตกลงกันด้วยปาก **ลงไฟล์** ทันที | ข้อตกลงที่พูดกันเฉยๆ หายไปใน 3 วัน |
| อ่านโค้ดคนอื่นบ้างแม้ไม่ใช่ส่วนตัวเอง | ลด bus factor — คนหนึ่งหายไปแล้วทีมไม่ตาย |
| แก้ conflict ทันทีที่รู้ | conflict ไม่หายไปเอง มีแต่โตขึ้น |
| ถามเร็ว | ติด 3 ชั่วโมงกับติด 20 นาที ต่างกันแค่กล้าถามหรือเปล่า |

---

## ส่วนที่ 4 — ช่องว่างของ LUMA และควรอุดข้อไหน

| สิ่งที่ทีมจริงมี | LUMA | ควรทำไหมสำหรับทีม 3 คน |
|---|---|---|
| แยก service ตามสิ่งที่ deploy | ✅ | — |
| dependency ล็อกเวอร์ชัน | ✅ | — |
| test ต่อ service | ✅ โครงพร้อม | — |
| สัญญา API เขียนก่อนโค้ด | ✅ | — |
| mock service | ✅ | — |
| ตัวตรวจอัตโนมัติ + pre-commit | ✅ | — |
| บันทึกการตัดสินใจ (ADR) | ✅ | — |
| **`CODEOWNERS`** | ❌ | ✅ **ควรทำ** — 6 บรรทัด ได้ผู้รีวิวอัตโนมัติ |
| **PR template** | ❌ | ✅ **ควรทำ** — checklist สั้นๆ กัน PR ครึ่งๆ กลางๆ |
| **Issue template** | ❌ | 🟡 ทำก็ดี ไม่ทำก็ได้ |
| **GitHub Actions CI** | ❌ (มี hook ในเครื่อง) | 🟡 ถ้าเหลือเวลา — hook พอสำหรับตอนนี้ |
| label อัตโนมัติตาม path | ❌ | 🟡 มี label 19 อันแล้ว ติดเองได้ |
| `CODEMAP.md` / `GLOSSARY.md` | ❌ | 🟡 `README.md` + `ARCHITECTURE.md` ทำหน้าที่นี้อยู่แล้ว |
| conventional commits บังคับ | ❌ | ❌ **ไม่ต้อง** — ใช้ `feat:` `fix:` `docs:` กันเองพอ |
| ชั้น `repositories/` | ❌ | ❌ **ไม่ต้อง** — เอาแค่กฎ "routes ห้าม query เอง" |
| Docker / compose | ❌ | ❌ **ไม่ต้อง** — อาจารย์ให้แยกเครื่องจริง ไม่ใช่ container |
| e2e test | ❌ | ❌ **ไม่ต้อง** — เกินขอบเขตวิชา |

**บทเรียนสำคัญที่สุดจากการสำรวจนี้**

> ทีมใหญ่มีกลไกเยอะเพราะ **จำนวนคนทำให้การคุยกันตรงๆ เป็นไปไม่ได้**
> immich มี workflow 23 ไฟล์ เพราะรับ PR จากคนแปลกหน้าทั่วโลกที่คุยกันไม่ได้
>
> ทีม 3 คนที่คุยกันได้ **ไม่ควรลอกกลไกมาทั้งหมด** — จะกลายเป็นพิธีกรรมที่กินเวลา
> ไปจากการทำงานจริง
>
> ให้เอาเฉพาะกลไกที่แก้ปัญหาที่ทีมเรามีจริง ซึ่งมี 3 อย่าง:
> **เจ้าของที่ชัดเจน (CODEOWNERS)** · **สัญญาที่ตกลงก่อน (API_CONTRACT + mock)** ·
> **กติกาที่เครื่องบังคับแทนคน (check_all)**
>
> ที่เหลือคือ **การคุยกันสัปดาห์ละครั้ง** ซึ่งได้ผลกว่าเครื่องมือทุกตัวรวมกัน

---

## แหล่งอ้างอิง

**โครงสร้าง repo จริง** (ดึงผ่าน GitHub API เมื่อ 18 ส.ค. 2026)

- [immich-app/immich](https://github.com/immich-app/immich) — โครงสร้าง · `CODEOWNERS` · `.github/workflows` · PR template · `labeler.yml`
- [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) — ต้นทางของ Forge
- [photoprism/photoprism](https://github.com/photoprism/photoprism) — `CODEMAP.md` · `GLOSSARY.md`
- [invoke-ai/InvokeAI](https://github.com/invoke-ai/InvokeAI) — `AGENTS.md` · `CODEOWNERS`
- [Sanster/IOPaint](https://github.com/Sanster/IOPaint) — โครงเล็กแบบ Python + web

**ขนาด PR กับคุณภาพการรีวิว**

- [The Impact of PR Size on Code Review Quality — Propel Code](https://www.propelcode.ai/blog/pr-size-impact-code-review-quality-data-study)
- [Pull requests should have less than 200 changed lines — Bruno Arine](https://brunoarine.com/blog/pull-requests-should-have-less-than-200-cl/)
- [Proof your thousand-line pull requests result in more bugs — tekin.co.uk](https://tekin.co.uk/2020/05/proof-your-thousand-line-pull-requests-create-more-bugs)
- [Pull Request Size: Ideal Limits — Engineering Manager Tools](https://www.em-tools.io/engineering-metrics/pull-request-size)

**รูปแบบการแตกกิ่ง**

- [How to Choose GitFlow vs Trunk-Based in 7 Steps (2026) — GitKraken](https://www.gitkraken.com/blog/how-to-choose-gitflow-vs-trunk-based-in-7-steps-2026)
- [Trunk-Based Development vs Gitflow — Mergify](https://mergify.com/blog/trunk-based-development-vs-gitflow-which-branching-model-actually-works)
- [Trunk-Based Development vs Git Flow — Assembla](https://get.assembla.com/blog/trunk-based-development-vs-git-flow/)
- [GitFlow vs GitHub Flow vs Trunk-Based — codewithmukesh](https://codewithmukesh.com/blog/git-workflows-gitflow-vs-github-flow-vs-trunk-based-development/)

**monorepo กับการแบ่ง repo**

- [Monorepo vs. multi-repo — Thoughtworks](https://www.thoughtworks.com/insights/blog/agile-engineering-practices/monorepo-vs-multirepo)
- [Monorepo vs Multi-Repo — Kinsta](https://kinsta.com/blog/monorepo-vs-multi-repo/)
- [Monorepo vs. Polyrepo — Spacelift](https://spacelift.io/blog/monorepo-vs-polyrepo)

**merge conflict และการทำงานคู่ขนาน**

- [Avoid Merge Conflicts: The Developer's Guide to Peaceful Git — Mergify](https://articles.mergify.com/avoid-merge-conflicts/)
- [Vertical Slice Architecture for Web Apps — Clean Code Guy](https://cleancodeguy.com/blog/vertical-slice-architecture)
- [Best Practices for Handling Code Merging and Conflicts — PixelFreeStudio](https://blog.pixelfreestudio.com/best-practices-for-handling-code-merging-and-conflicts/)

**โครงสร้าง Flask**

- [The Flask Mega-Tutorial, Part XV: A Better Application Structure — Miguel Grinberg](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure)
- [How to Structure Large Flask Applications — OneUptime](https://oneuptime.com/blog/post/2026-01-26-flask-large-applications/view)
- [Building Scalable Flask Applications with Blueprints and Application Factories — Leapcell](https://leapcell.io/blog/building-scalable-flask-applications-with-blueprints-and-application-factories)

---

## อ่านต่อในโปรเจกต์นี้

- [`TEAM_AND_WORKFLOW.md`](TEAM_AND_WORKFLOW.md) — ข้อตกลงของทีมเราเอง
- [`DECISIONS.md`](DECISIONS.md) — บันทึกการตัดสินใจ (ADR)
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — สถาปัตยกรรม 3 เครื่อง
- [`API_CONTRACT.md`](API_CONTRACT.md) — สัญญาระหว่าง service
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) — วิธีส่งงาน
