# 05 — เอาแพตเทิร์นจากไฟล์ 01-04 มาใช้กับตารางจริงของ LUMA
#
# ตาราง users ในสไลด์คือของฝึกมือ ส่วนของจริงที่ต้องทำคือตาราง assets
# ตาม issue #45 (Walking Skeleton) ซึ่งมี 4 คอลัมน์:
#     id · prompt · file_path · created_at
#
# ไฟล์นี้ทำครบวงจรเดิม (สร้าง → ใส่ → อ่าน) บนหัวตารางชุดใหม่
# เพื่อให้เห็นว่าที่ซ้อมมาใช้กับงานจริงยังไง
#
# ⚠️ ไฟล์นี้ยังเป็นแค่ที่ซ้อม ไม่ใช่ของจริง — ดูหัวข้อ "3 ข้อที่ของจริงต่าง" ท้ายไฟล์

import os
import sqlite3
from datetime import datetime, timedelta, timezone

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "study.db")   # ไฟล์เดียวกับ 01-04 แค่เพิ่มตารางใหม่

conn = sqlite3.connect(db_path)

# PRAGMA foreign_keys ต้องสั่งใหม่ทุก connection — SQLite ปิดไว้เป็นค่าเริ่มต้น
# ตอนนี้ตาราง assets ยังไม่มี FOREIGN KEY เลยยังไม่มีผลอะไร
# แต่พอ #45 ต่อยอดเป็น assets.user_id → users.id เมื่อไหร่ ถ้าลืมบรรทัดนี้
# SQLite จะยอมให้มี asset ที่ชี้ไปหา user ที่ไม่มีอยู่จริง โดยไม่เตือนเลย
conn.execute("PRAGMA foreign_keys = ON;")


# ==================================================================
# CREATE — หัวตารางของ assets
# ==================================================================
conn.execute(
    """
    CREATE TABLE IF NOT EXISTS assets (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt     TEXT NOT NULL,
        file_path  TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """
)
conn.commit()

# ------------------------------------------------------------------
# ทำไม created_at เป็น TEXT ไม่ใช่ DATETIME
#
# SQLite ไม่มีชนิด DATETIME จริงๆ (เขียน DATETIME ลงไปก็ได้ แต่มันเก็บเป็น TEXT ให้อยู่ดี)
# วิธีที่ใช้กันคือเก็บเป็นสตริงรูปแบบ ISO 8601 'YYYY-MM-DD HH:MM:SS'
#
# ที่เลือกรูปแบบนี้เพราะมันเรียงลำดับแบบสตริงแล้วได้ผลตรงกับเรียงตามเวลาพอดี
# (ปีอยู่หน้า เดือนเป็นเลข 2 หลักเสมอ) → ORDER BY created_at DESC ใช้ได้เลย
# ถ้าเก็บเป็น '24/8/2026' จะเรียงผิดทันที เพราะ '3/1/2027' < '24/8/2026' ในเชิงสตริง
#
# และรูปแบบนี้ย้ายไป PostgreSQL ได้ตรงๆ ตอนขึ้นแบบ 4 เครื่อง (ดู ../README.md)
#
# DEFAULT (datetime('now')) = ถ้า INSERT ไม่ส่ง created_at มา SQLite ใส่เวลาปัจจุบัน
# (เป็นเวลา UTC) ให้เอง
# ------------------------------------------------------------------


# ==================================================================
# INSERT — asset จำลอง 8 ชิ้น
# ==================================================================
mock_prompts = [
    ("a neon cyberpunk street at night, rain reflections", "cyberpunk-street.png"),
    ("portrait of a cat wearing a tiny astronaut helmet",  "cat-astronaut.png"),
    ("watercolor mountains at sunrise, soft pastel",       "mountain-sunrise.png"),
    ("isometric coffee shop, cozy warm light",             "coffee-shop-iso.png"),
    ("minimal logo, blue circle, flat vector",             "logo-blue-circle.png"),
    ("old library with floating books, magic dust",        "magic-library.png"),
    ("retro 80s poster, palm trees, sunset gradient",      "retro-80s.png"),
    ("close-up macro of a dew drop on green leaf",         "dew-drop-macro.png"),
]

# สร้าง created_at ให้ห่างกันชิ้นละ 3 ชั่วโมง ไล่จากเก่า→ใหม่
# ถ้าปล่อยให้ DEFAULT datetime('now') ใส่ให้ทั้ง 8 แถว จะได้เวลาเดียวกันหมด
# แล้ว ORDER BY created_at DESC จะไม่เห็นผลอะไรเลย
#
# datetime.now(timezone.utc) — ไม่ใช้ datetime.utcnow() ที่ deprecated ไปแล้ว
# (utcnow() คืนเวลา UTC แต่ไม่ติด timezone มาด้วย ทำให้เอาไปเทียบกับเวลาอื่นแล้วเพี้ยน)
now = datetime.now(timezone.utc)

assets = [
    {
        "prompt": prompt,
        "file_path": f"static/uploads/{filename}",
        # strftime ให้ตรงรูปแบบที่ datetime('now') ของ SQLite ใช้ ห้ามผสมรูปแบบกัน
        "created_at": (now - timedelta(hours=3 * (len(mock_prompts) - i)))
                      .strftime("%Y-%m-%d %H:%M:%S"),
    }
    for i, (prompt, filename) in enumerate(mock_prompts)
]

# named parameter เหมือนเดิมทุกไฟล์ — ห้ามต่อสตริงประกอบ SQL (ADR-008)
# prompt เป็นข้อความอิสระที่ผู้ใช้พิมพ์เอง มีเครื่องหมาย ' ปนมาได้ตลอด
# ยิ่งต้องผูกเป็น parameter
conn.executemany(
    """
    INSERT INTO assets (prompt, file_path, created_at)
    VALUES (:prompt, :file_path, :created_at)
    """,
    assets,
)
conn.commit()


# ==================================================================
# READ — asset ใหม่→เก่า
# ==================================================================
conn.row_factory = sqlite3.Row

print("=" * 74)
print("assets — เรียงจากใหม่ไปเก่า (ORDER BY created_at DESC)")
print("=" * 74)

# นี่คือ query แถวแรกของตาราง "Query ที่จะต้องเขียน" ใน ../README.md
# ("asset ของ user เรียงใหม่→เก่า") แค่ยังไม่มีเงื่อนไข WHERE user_id
# เพราะ #45 ยังไม่ผูก assets เข้ากับ users
for a in conn.execute(
    """
    SELECT id, prompt, file_path, created_at
    FROM assets
    ORDER BY created_at DESC
    LIMIT 5
    """
):
    print(f"  #{a['id']:<3} {a['created_at']}  {a['prompt'][:38]:<38}")
    print(f"       {a['file_path']}")

total = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
print(f"\nตาราง assets มีทั้งหมด {total} แถว")

conn.close()

# ==================================================================
# 3 ข้อที่ของจริงต่างจากไฟล์นี้
# ==================================================================
# 1. CREATE TABLE ของจริงไม่ฝังอยู่ในสคริปต์ Python
#    ต้องอยู่ใน ../schema/*.sql และเปลี่ยนผ่าน migration เท่านั้น (ADR-008)
#    เหตุผลอยู่ใน ../README.md: v1 พึ่ง db.create_all() ซึ่งไม่ ALTER ตารางที่มีแล้ว
#    พอ PR เพิ่มคอลัมน์ → test ล้ม 3 ข้อ เพราะไฟล์ .db เก่ายังเป็น schema เดิม
#
# 2. รันไฟล์นี้ซ้ำจะได้ asset เพิ่มอีก 8 ชิ้นทุกรอบ
#    ต่างจาก 02-insert-mock.py ที่กันไว้ด้วย INSERT OR IGNORE + email UNIQUE
#    ตาราง assets ไม่มีคอลัมน์ไหนเป็น UNIQUE เลยไม่มีอะไรให้ SQLite ใช้ตัดสินว่าซ้ำ
#    → prompt เดียวกันสร้างซ้ำได้จริงในระบบ (สร้างภาพใหม่จาก prompt เดิม) จึงถูกต้องแล้ว
#      แต่แปลว่าตอนใส่ seed จริงต้องมีวิธีล้างของเก่าก่อน
#
# 3. ของจริงจะมี FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
#    และตาราง tags / asset_tags แยกต่างหาก (ไม่เก็บ tag เป็นสตริงคั่นด้วย comma
#    แบบ v1 เพราะค้นหาไม่ได้จริง) — รายละเอียดอยู่ใน ../README.md

print("\nซ้อมครบแล้ว — ของจริงอยู่ที่ issue #45 (schema/ + migrations/)")
