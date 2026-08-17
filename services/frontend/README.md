# frontend/ — หน้าเว็บ (HTML / CSS / JS)

👤 คนที่ 1 — Web Platform
**เครื่อง**: 192.168.1.10 (ตัวอย่าง)

## หน้าที่

หน้าตาทั้งหมดที่ผู้ใช้เห็น — เรียก backend ผ่าน `fetch()` ไปที่ API base URL ที่อ่านจาก config

## ไม่ต้องลง Python package

service นี้เป็น HTML / CSS / JS ล้วน จึง **ไม่มี `requirements.txt`**
เครื่อง frontend (192.168.1.10) ไม่ต้องลง OpenCV, Flask หรืออะไรเลย

**ตอน dev** เสิร์ฟด้วย web server ที่ติดมากับ Python ได้เลย:
```bash
cd services/frontend
python -m http.server 8080
```

**ตอน V5** Nginx เสิร์ฟให้ — ดู [`../../deploy/README.md`](../../deploy/README.md)

> ช่วง V1–V3 ไฟล์หน้าเว็บยังอยู่ที่ `../backend/app/templates/` เพราะ Flask render ให้
> จะย้ายมาที่นี่ตอน V4 (ดู issue V4 ใน `docs/ROADMAP.md`)

## โครงสร้างที่ตั้งใจไว้

```
frontend/
├── pages/      HTML แต่ละหน้า (index, login, register, dashboard, canvas, hub)
├── css/        stylesheet
├── js/         โค้ด JS (api client, smart canvas, gallery)
└── assets/     ไอคอน / รูปประกอบ
```

## V1–V3 กับ V4 ต่างกันอย่างไร

- **V1–V3**: Flask render Jinja2 template → ไฟล์อยู่ที่ `backend/app/templates/`
- **V4 ขึ้นไป**: แยกออกมาเป็น static file ในโฟลเดอร์นี้ เสิร์ฟจากเครื่องคนละเครื่อง
  → ตอนนั้น `fetch()` จะเป็น cross-origin ต้องตั้ง CORS ที่ backend ด้วย

> เขียน JS โดยคิดล่วงหน้าว่า API base URL จะเปลี่ยน — เก็บไว้ที่เดียว
> เช่น `const API_BASE = window.LUMA_CONFIG.apiBase;` ไม่ใช่ hardcode `/api` กระจายทั่วไฟล์

## ข้อกำหนด UI/UX จากอาจารย์ (Lecture 4 หน้า 53)

> **Minimalist & Flexible Interface**: หน้าตาแอปปรับเปลี่ยนตามโหมดที่ใช้ เพื่อไม่ให้รกสายตา

## สิ่งที่ต้องระวัง (บทเรียนจาก v1)

- [ ] ข้อความจากผู้ใช้ (เช่น prompt) แสดงด้วย **`textContent` ไม่ใช่ `innerHTML`** — กัน stored XSS
- [ ] `[hidden] { display: none !important; }` — ไม่งั้นกฎที่มาทีหลัง (เช่น `.spinner`)
      จะ override `[hidden]` แล้ว element โชว์ทั้งที่ควรซ่อน
- [ ] ระวัง **CSS specificity** เวลาทำปุ่มให้หน้าตาเหมือนลิงก์ — `.nav-link-btn` (0,1,0)
      แพ้ `button[type="submit"]` (0,1,1) เคยทำให้ปุ่ม Logout เพี้ยนใน v1
- [ ] ใช้ `.class` สำหรับ styling เก็บ `#id` ไว้ให้ JavaScript (Lecture 5 หน้า 121)

## อ้างอิงในสไลด์ + เครื่องมือ

- HTML structure, elements, tags, attributes: **Lecture 5 หน้า 76–106**
- CSS: selector (element/class/id), inheritance, inline/internal/external,
  pseudo-class, box model: **Lecture 5 หน้า 107–128**
- Responsive web design: Lecture 4 หน้า 67
- [htmlcheatsheet.com](https://htmlcheatsheet.com/) — tag reference, generator
- [angrytools.com/css/animation](https://angrytools.com/css/animation/) — สร้าง CSS animation
