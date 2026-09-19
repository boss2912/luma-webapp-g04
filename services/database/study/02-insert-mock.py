# 02 — ใส่ข้อมูลจำลอง (INSERT)
#
# สร้างตารางเปล่าไว้แล้วยังดูอะไรไม่ออก ต้องมีข้อมูลก่อนถึงจะเห็นว่า
# ORDER BY / GROUP BY / WHERE ทำงานยังไง
#
# ไฟล์นี้ใส่ 2 ชุด:
#   ชุดที่ 1 — 3 แถวจากสไลด์เป๊ะๆ (Alice / Bob / John Doe) ไว้เทียบภาพ
#   ชุดที่ 2 — 20 แถวสุ่ม ไว้ให้ query ในไฟล์ 03 มีอะไรให้เรียง/ให้จัดกลุ่มจริงๆ
#
# ต้องรัน 01-create-table.py มาก่อน

import os
import random
import sqlite3

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "study.db")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ------------------------------------------------------------------
# ชุดที่ 1 — 3 แถวตามสไลด์รูปที่ 2 (Read)
#
# ⚠️ สังเกตคอลัมน์ accuracy ในสไลด์: Alice = 0.8, Bob = 0.9, John Doe = 95.5
#    Alice กับ Bob ดูเป็น "สัดส่วน" (0.0-1.0) แต่ John Doe ดูเป็น "เปอร์เซ็นต์"
#    → คนละหน่วยกันอยู่ในคอลัมน์เดียวกัน
#
#    ฐานข้อมูลไม่ห้าม เพราะชนิด REAL รับตัวเลขทศนิยมได้ทุกค่า
#    แปลว่า "ชนิดข้อมูลถูก" ไม่ได้แปลว่า "ข้อมูลถูก"
#    ความหมายของคอลัมน์ (หน่วย ช่วงค่า) เป็นสิ่งที่ทีมต้องตกลงกันเอง
#    แล้วบังคับด้วย CHECK constraint หรือด้วยโค้ดฝั่งที่เขียนข้อมูลลงไป
#
#    เก็บ 3 แถวนี้ไว้ตามสไลด์เพื่อให้เทียบภาพได้ แต่ 20 แถวข้างล่างจะใช้
#    สเกล 0.0-1.0 อย่างเดียว
# ------------------------------------------------------------------
slide_users = [
    {"name": "Alice",    "email": "alice@example.com",    "points": 100, "accuracy": 0.8},
    {"name": "Bob",      "email": "bob@example.com",      "points": 150, "accuracy": 0.9},
    {"name": "John Doe", "email": "john.doe@example.com", "points": 50,  "accuracy": 95.5},
]

# ------------------------------------------------------------------
# named parameter — ตัวแปรเขียนเป็น :name :email :points :accuracy
# แล้วส่งค่าไปเป็น dict แยกต่างหาก
#
# ⛔ ห้ามเขียนแบบนี้เด็ดขาด:
#       cursor.execute(f"INSERT INTO users (name) VALUES ('{name}')")
#    เหตุผล 2 ข้อ:
#    1. ถ้า name มีเครื่องหมาย ' อยู่ (เช่น O'Brien) คำสั่งจะพัง
#       และถ้าเป็นข้อมูลจากผู้ใช้ เขาจะแอบต่อคำสั่ง SQL เข้ามาได้ (SQL injection)
#    2. ตัวเลข/None จะถูกแปลงเป็นสตริงไปหมด ชนิดข้อมูลในตารางจะเพี้ยน
#
#    ใช้ :name แล้ว sqlite3 จะส่งค่าแยกจากคำสั่ง SQL ทำให้ค่านั้น
#    เป็น "ข้อมูล" เสมอ ไม่มีทางกลายเป็น "คำสั่ง" — เป็นกติกาของโปรเจกต์นี้ (ADR-008)
#
# INSERT OR IGNORE — ถ้าอีเมลซ้ำกับที่มีอยู่แล้ว ให้ข้ามแถวนั้นเงียบๆ
# แทนที่จะโยน IntegrityError ทำให้รันไฟล์นี้ซ้ำกี่รอบก็ได้ข้อมูลชุดเดิม
# (ที่ทำแบบนี้ได้เพราะเราตั้ง email เป็น UNIQUE ไว้ในไฟล์ 01)
# ------------------------------------------------------------------
INSERT_SQL = """
    INSERT OR IGNORE INTO users (name, email, points, accuracy)
    VALUES (:name, :email, :points, :accuracy)
"""

# ใส่ทีละแถวด้วย execute() — เห็นชัดว่าแต่ละแถวเกิดอะไรขึ้น
for user in slide_users:
    cursor.execute(INSERT_SQL, user)
    print(f"ใส่ {user['name']:<10} -> เพิ่มจริง {cursor.rowcount} แถว")

# ------------------------------------------------------------------
# ชุดที่ 2 — 20 แถวสุ่ม
#
# random.Random(42) = สุ่มแบบ "seed คงที่" รันกี่ครั้งก็ได้ชุดเดิมทุกครั้ง
# สำคัญมากเวลาซ้อม เพราะถ้าข้อมูลเปลี่ยนทุกรอบ จะแยกไม่ออกว่าผลที่ต่างไป
# เกิดจาก query ที่เราเพิ่งแก้ หรือเกิดจากข้อมูลที่บังเอิญเปลี่ยน
# ------------------------------------------------------------------
rng = random.Random(42)

first_names = ["Nan", "Ploy", "Beam", "Tar", "Mint", "Ohm", "Fay", "Gun",
               "June", "Kae", "Nut", "Oat", "Prim", "Ryu", "Som", "Tan",
               "Ubon", "Van", "Wit", "Yok"]

mock_users = [
    {
        "name": name,
        "email": f"{name.lower()}@example.com",
        "points": rng.randint(0, 200),
        "accuracy": round(rng.uniform(0.0, 1.0), 2),  # สเกลเดียวกันหมด 0.0-1.0
    }
    for name in first_names
]

# executemany() = ส่ง SQL ไปคำสั่งเดียว แล้วป้อนค่าให้เป็นชุด
# ต่างจากการวน execute() ทีละแถวตรงที่ SQLite แปลคำสั่ง SQL แค่ครั้งเดียว
# พอข้อมูลเยอะๆ จะเร็วกว่าชัดเจน
cursor.executemany(INSERT_SQL, mock_users)
print(f"\nใส่ชุดสุ่ม 20 แถว -> เพิ่มจริง {cursor.rowcount} แถว")

# ------------------------------------------------------------------
# commit() = ยืนยันการเปลี่ยนแปลง
# ถ้าไม่เรียก แล้ว close() ไป ข้อมูลที่เพิ่ง INSERT จะหายหมด
# เพราะ sqlite3 เปิด transaction ให้อัตโนมัติแล้วรอคำสั่งยืนยัน
# ------------------------------------------------------------------
conn.commit()

total = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
print(f"ตอนนี้ตาราง users มีทั้งหมด {total} แถว")

conn.close()

print("\nขั้นต่อไป: python 03-read.py  (หรือเปิด study.db ใน DB Browser ดูเลยก็ได้)")
