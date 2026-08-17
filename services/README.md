# services/ — แยกตามเครื่องที่รันจริง

แต่ละโฟลเดอร์ในนี้คือ **1 service ที่รันแยกเครื่องได้** ตามสเปก distributed system
ของอาจารย์ (Lecture 4 หน้า 54, 56) — ดู `docs/COURSE_REQUIREMENTS.md` ข้อ 4

| โฟลเดอร์ | บทบาท | เครื่อง (ตัวอย่าง IP) | ผู้ดูแล |
|---|---|---|---|
| `backend/` | Flask — API, Auth, Logging | 192.168.1.20 | 👤 คนที่ 1 — Web Platform (บอส) |
| `frontend/` | HTML / CSS / JS | 192.168.1.10 | 👤 คนที่ 1 — Web Platform (บอส) |
| `ai-engine/` | Forge AI + Image Processing pipeline | 192.168.1.30 | 👤 คนที่ 3 — AI + Image Processing Engine |
| `database/` | SQLite schema / migrations / queries | 192.168.1.20 (เครื่องเดียวกับ backend) | 👤 คนที่ 2 — Data & Storage |

## กฎเหล็ก

1. **ห้าม hardcode `localhost` หรือ IP ใดๆ ในโค้ด** — อ่านจาก config/env เสมอ
   (Lecture 4 หน้า 54: *"ให้ใช้ความรู้จากรายวิชา Network เพื่อทำให้ PCs เชื่อมโยงกัน"*)
2. service คุยกันผ่าน **HTTP API เท่านั้น** ไม่ import โค้ดข้าม service
   เพราะตอน V4/V5 มันจะอยู่คนละเครื่องจริง
3. แต่ละ service มี `requirements.txt` ของตัวเอง — เครื่อง frontend ไม่ต้องลง OpenCV
4. `requirements.txt` ทุกไฟล์ **ใช้ ASCII เท่านั้น** (คอมเมนต์ไทยทำให้ pip พังบนเครื่อง
   locale ไทย — ดู `archive/ARCHITECTURE_v1.md` ปัญหา B)

## ตอนนี้ยังว่างอยู่

โครงสร้างนี้ถูกวางไว้ล่วงหน้าให้ครบถึง V5 แต่ยังไม่มีโค้ด
งานเริ่มจาก **V2 (Flask + SQLite)** ตาม `docs/ROADMAP.md`
