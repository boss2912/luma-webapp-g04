# 🤝 Contributing Guide — LUMA Web App (Group 04)

> ภาษาไทย · English (bilingual guide for the team)

---

## 🌿 Git Branching Strategy

### โครงสร้าง Branch / Branch Structure

```
main     ────────────────────────────────● ← release เท่านั้น / release only
                                         ↑ PR only (หัวหน้า approve)
develop  ──●──●──●──●──●──●──●──●──●──●─● ← รวมงานทีม / integration branch
           ↑       ↑       ↑
           │   feature/forge-ai
           │               ↑
feature/backend-auth    feature/ui-frontend
```

### กฎเหล็ก / Non-Negotiable Rules

| 🇹🇭 ภาษาไทย | 🇬🇧 English |
|------------|-----------|
| ❌ ห้าม push ตรงเข้า `main` หรือ `develop` | ❌ Never push directly to `main` or `develop` |
| ✅ ต้องเปิด Pull Request ทุกครั้ง | ✅ Always open a Pull Request |
| ✅ ต้องมีคน review อย่างน้อย 1 คน | ✅ At least 1 reviewer required |
| ✅ sync `develop` กลับเข้า branch ตัวเองสัปดาห์ละครั้ง | ✅ Sync `develop` into your branch weekly |

---

## 👤 Branch ของแต่ละคน / Branch Assignment

| คน / Person | Branch | หน้าที่ / Responsibility |
|-------------|--------|------------------------|
| คุณ (หัวหน้า) / Team Lead | `feature/backend-auth` | Flask Backend, Auth, API, DB |
| คนที่ 2 / Member 2 | `feature/forge-ai` | Forge AI integration, Testing |
| คนที่ 3 / Member 3 | `feature/ui-frontend` | Templates, CSS, JavaScript |

---

## 📋 Workflow ประจำวัน / Daily Workflow

### 1. เริ่มวันทำงาน / Start of Day

```bash
# อัปเดต develop ล่าสุดก่อน / Always pull latest develop first
git checkout develop
git pull origin develop

# กลับไป branch ตัวเอง แล้ว sync develop / Go back to your branch and sync
git checkout feature/your-feature
git merge develop
# ถ้ามี conflict → แก้แล้วรัน: git add . && git commit -m "merge: sync develop"
```

### 2. ระหว่างทำงาน / During Work

```bash
# บันทึกงาน / Save your work
git add .
git commit -m "feat: อธิบายสั้นๆ / brief description"

# Push ขึ้น branch ตัวเอง / Push to your branch
git push origin feature/your-feature
```

### 3. ส่งงาน / Submit Work (PR)

```bash
# ตรวจสอบก่อน push / Check before pushing
git status                          # ต้องไม่มี instance/config.py, *.db
git log --oneline -5                # commit message อ่านรู้เรื่อง
python run.py                       # รันได้โดยไม่ error
```

จากนั้นไปที่ GitHub → Pull requests → New pull request:
- **base:** `develop`  ← **compare:** `feature/your-feature`
- เขียน description: ทำอะไร, ทดสอบอะไรแล้ว, screenshot (ถ้ามี)
- Assign reviewer: `boss2912` (หัวหน้า)

### 4. ส่งงานจริง / Release (หัวหน้าเท่านั้น / Lead only)

```bash
# เปิด PR: develop → main บน GitHub web เท่านั้น
# ห้าม git push ตรงเข้า main
```

---

## 📝 Commit Message Format

```
<type>: <short description in Thai or English>
```

| Type | ใช้เมื่อ / When to use |
|------|----------------------|
| `feat:` | เพิ่ม feature ใหม่ / New feature |
| `fix:` | แก้ bug / Bug fix |
| `docs:` | แก้ documentation / Documentation change |
| `style:` | แก้ CSS, format / Style/format change |
| `refactor:` | ปรับโครงสร้าง ไม่เพิ่ม feature / Refactor without new feature |
| `test:` | เพิ่ม/แก้ test / Test changes |
| `chore:` | งาน maintenance / Maintenance tasks |

**ตัวอย่าง / Examples:**
```bash
git commit -m "feat: เพิ่มระบบ login/register ครบวงจร"
git commit -m "fix: แก้ FORGE_AI_ENDPOINT อ่านจาก config แทน hardcode"
git commit -m "style: ปรับ CSS dashboard ให้ responsive"
git commit -m "docs: เพิ่ม API endpoint docs ใน README"
```

---

## ✅ Self-Review Checklist (ก่อน Push ทุกครั้ง)

```
[ ] git status ไม่มี instance/config.py, *.db, .venv/ ในรายการ
[ ] python run.py รันได้โดยไม่มี error
[ ] ถ้าแก้ models.py → ทดสอบ db.create_all() ใหม่
[ ] commit message อ่านแล้วเข้าใจว่าทำอะไร
[ ] ไม่ hardcode IP, password, API key ในโค้ด
```

---

## 🆘 แก้ปัญหาที่พบบ่อย / Common Issues

| ปัญหา / Problem | วิธีแก้ / Solution |
|----------------|-------------------|
| `ModuleNotFoundError: flask` | `pip install -r requirements.txt` |
| `502 Forge AI ไม่ตอบสนอง` | เช็ค `FORGE_AI_ENDPOINT` ใน config, เช็คว่า SD WebUI รันอยู่ |
| Merge conflict ใน templates | ติดต่อหัวหน้า (boss2912) ก่อนแก้ |
| `instance/luma.db` หายไป | ปกติ — สร้างใหม่เองโดยรัน `python run.py` |
| ลืม pull develop ก่อนทำงาน | `git checkout develop && git pull && git checkout feature/... && git merge develop` |
