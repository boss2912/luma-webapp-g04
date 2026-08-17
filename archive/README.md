# archive/ — บันทึกโค้ด v1 ที่ถูกลบออก

โฟลเดอร์นี้เก็บ **ความรู้** จากโค้ดชุดแรก ไม่ใช่โค้ดที่รันได้
มีไว้เพื่อไม่ต้องขุด git history เวลาอยากรู้ว่า "ตอนนั้นเราแก้เรื่องนี้ไว้อย่างไร"

| ไฟล์ | เนื้อหา |
|---|---|
| `CODE_SNAPSHOT_v1.md` | **source ทั้งหมดของ `luma-webapp/` แบบคำต่อคำ** 32 ไฟล์ |
| `ARCHITECTURE_v1.md` | v1 ทำงานอย่างไร · อะไรควรหยิบกลับมาใช้ · ปัญหา 6 ข้อที่เจอ |
| `SECURITY_FIXES_v1.md` | ช่องโหว่ F01–F15 + checklist สำหรับ review PR |

## โค้ดตัวจริงยังอยู่ใน git

### ใช้ `backup/v1-final` เสมอ

```bash
git show backup/v1-final:luma-webapp/app/routes/api.py
git checkout backup/v1-final -- luma-webapp/       # ดึงกลับมาทั้งโฟลเดอร์
```

`backup/v1-final` คือ commit สุดท้ายที่โค้ด v1 **ครบและทำงานได้จริง** —
รวม PR #10/#11/#12 แล้วและ `pytest` ผ่าน 33/33

> ⚠️ ถ้าดึงโค้ดกลับมารัน test **ต้องลบ `luma-webapp/instance/luma.db` ออกก่อน**
> เพราะ schema ในไฟล์นั้นเก่ากว่า models และ `db.create_all()` ไม่ ALTER ตารางเดิม

### tag ทั้งหมด

| tag | ชี้ไปที่ | มี security fix F01–F15? | ไฟล์ test |
|---|---|---|---|
| **`backup/v1-final`** | **v1 สมบูรณ์ที่สุด — รวม 3 PR + test ผ่าน** | ✅ | 9 |
| `backup/pre-restructure-develop` | develop ในเครื่อง **ก่อน** merge 3 PR | ❌ | 2 |
| `backup/pre-restructure-main` | main ก่อนรีเซ็ต | ❌ | 0 |
| `backup/pr10-security` | branch `fix/security-and-issue9` | ✅ | 0 |
| `backup/pr11-forge-ai` | branch `feature/forge-ai-issue5-6` | ✅ | 6 |
| `backup/pr12-backend-auth` | branch `feature/backend-auth-issue2-3` | ✅ | 4 |

> ⚠️ **อย่าใช้ `backup/pre-restructure-develop` เป็นแหล่งอ้างอิงโค้ด** — มันชี้ไปที่ develop
> ในเครื่องก่อนที่ 3 PR จะถูก merge เข้ามา จึง**ไม่มี** CSRFProtect, rate limiter,
> การแก้ IDOR และ test ส่วนใหญ่ เก็บไว้เป็นแค่บันทึกว่า "ก่อนรีเซ็ตเครื่องอยู่สถานะไหน"

## สถานะของ v1 ตอนถูกเก็บ

รวม PR #10 + #11 + #12 แล้ว · **`pytest` 33/33 ผ่าน** (บนฐานข้อมูลใหม่)
ทำได้ถึงปลาย **V3** ตาม milestone ของอาจารย์ (Flask + SQLite + Forge)
