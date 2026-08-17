# archive/ — บันทึกโค้ด v1 ที่ถูกลบออก

โฟลเดอร์นี้เก็บ **ความรู้** จากโค้ดชุดแรก ไม่ใช่โค้ดที่รันได้
มีไว้เพื่อไม่ต้องขุด git history เวลาอยากรู้ว่า "ตอนนั้นเราแก้เรื่องนี้ไว้อย่างไร"

| ไฟล์ | เนื้อหา |
|---|---|
| `CODE_SNAPSHOT_v1.md` | **source ทั้งหมดของ `luma-webapp/` แบบคำต่อคำ** 32 ไฟล์ |
| `ARCHITECTURE_v1.md` | v1 ทำงานอย่างไร · อะไรควรหยิบกลับมาใช้ · ปัญหา 6 ข้อที่เจอ |
| `SECURITY_FIXES_v1.md` | ช่องโหว่ F01–F15 + checklist สำหรับ review PR |

## โค้ดตัวจริงยังอยู่ใน git

```bash
git show backup/pre-restructure-develop:luma-webapp/app/routes/api.py
git checkout backup/pre-restructure-develop -- luma-webapp/   # ดึงกลับมาทั้งโฟลเดอร์
```

| tag | ชี้ไปที่ |
|---|---|
| `backup/pre-restructure-develop` | develop ก่อนรีเซ็ต (มี PR #10/#11/#12 รวมแล้ว) |
| `backup/pre-restructure-main` | main ก่อนรีเซ็ต |
| `backup/pr10-security` | branch `fix/security-and-issue9` |
| `backup/pr11-forge-ai` | branch `feature/forge-ai-issue5-6` |
| `backup/pr12-backend-auth` | branch `feature/backend-auth-issue2-3` |

## สถานะของ v1 ตอนถูกเก็บ

รวม PR #10 + #11 + #12 แล้ว · **`pytest` 33/33 ผ่าน** (บนฐานข้อมูลใหม่)
ทำได้ถึงปลาย **V3** ตาม milestone ของอาจารย์ (Flask + SQLite + Forge)
