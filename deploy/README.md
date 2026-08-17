# deploy/ — Nginx และ config ต่อเครื่อง

👤 คนที่ 1 — Web Platform (บอส) (Nginx เป็นงาน V5)

## โครงสร้าง

```
deploy/
├── nginx/   nginx.conf + site config
└── env/     .env.example ของแต่ละเครื่อง (⛔ .env จริงห้าม commit)
```

## Nginx ทำอะไร (Lecture 4 หน้า 54)

Reverse proxy — รับ request จาก browser แล้วกระจาย (route) ต่อไปยัง Frontend หรือ Backend
ตาม path ที่กำหนด ผู้ใช้เห็น URL เดียวแม้เบื้องหลังจะเป็นหลายเครื่อง

```
Browser → Nginx ─┬→ /        → Frontend  192.168.1.10
                 └→ /api/    → Backend   192.168.1.20:5000
```

## แผนที่ IP (ตัวอย่างจากสไลด์ — ต้องแทนด้วย IP จริงตอน deploy)

| Service | IP ตัวอย่าง | พอร์ต |
|---|---|---|
| Frontend | 192.168.1.10 | 80 |
| Backend (Flask) | 192.168.1.20 | 5000 |
| Database (SQLite) | 192.168.1.20 | — (ไฟล์ในเครื่อง) |
| AI Server (Forge) | 192.168.1.30 | 7860 |

> `luma-project-spec.md` เตือนไว้: IP เหล่านี้เป็นตัวอย่างในวง LAN เดียวกัน
> **ต้องแทนที่ด้วย IP จริงของเครื่องแต่ละคนตอน deploy**

## ⚠️ เรื่องความปลอดภัยตอนข้ามเครื่อง

Flask dev server ต้อง bind `0.0.0.0` เพื่อให้เครื่องอื่นบน LAN เข้าถึงได้:
```
LUMA_HOST=0.0.0.0 python run.py
```

**ห้ามตั้ง `LUMA_DEBUG=1` พร้อมกัน** — Werkzeug debugger รันโค้ด Python จากหน้าเว็บได้
พอ bind ทุก interface = ทุกเครื่องบน network ยึดเครื่องได้ โดยไม่มีรหัสผ่านกั้น
(ดู F02 ใน `archive/SECURITY_FIXES_v1.md` — v1 เคย hardcode ทั้งสองอย่างไว้พร้อมกัน)

## Checklist ตอนทำ V4 (แยก frontend)

- [ ] frontend เรียก backend ข้าม origin แล้ว → ต้องตั้ง **CORS** ที่ backend
- [ ] cookie session ข้าม origin ต้องตั้ง `SameSite` / `credentials: 'include'` ให้ถูก
- [ ] API base URL ของ frontend อ่านจาก config ไม่ hardcode

## Checklist ตอนทำ V5 (Nginx)

- [ ] Nginx proxy `/api/` ไป backend, `/` ไป frontend
- [ ] `proxy_set_header X-Forwarded-For` / `X-Forwarded-Proto`
- [ ] `client_max_body_size` ให้พอสำหรับอัปโหลดภาพ
- [ ] timeout ให้พอกับเวลา generate ภาพ (Forge ใช้เวลานาน — v1 ตั้ง timeout 120 วิ)
- [ ] rate limiter ที่เป็น in-memory ใน Flask **ใช้ไม่ได้แล้ว** ถ้ามีหลาย worker
      ต้องย้ายไป Redis หรือทำที่ระดับ Nginx (ดู F14)
