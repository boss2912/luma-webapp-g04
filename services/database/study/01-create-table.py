# 01 — หัวตาราง (schema) ต้องมีอะไรบ้าง
#
# สไลด์รูปที่ 1 (Create) โชว์ตาราง users ใน DB Browser ไว้ว่าหน้าตาแบบนี้:
#     id       INTEGER   "id" INTEGER
#     name     TEXT      "name" TEXT NOT NULL
#     email    TEXT      "email" TEXT NOT NULL UNIQUE
#     points   INTEGER   "points" INTEGER DEFAULT 0
#     accuracy REAL      "accuracy" REAL DEFAULT 0.0
#
# ไฟล์นี้สร้างตารางนั้นให้เหมือนเป๊ะ แล้วอ่านหัวตารางกลับมา print
# เพื่อให้เทียบกับภาพในสไลด์ได้ตรงๆ ว่าตรงกันจริงไหม

import os
import sqlite3

# path ของไฟล์ .db อิงจากตำแหน่งของสคริปต์นี้เสมอ ไม่ใช่ตำแหน่งที่รันคำสั่ง
# (เหตุผลอยู่ใน README.md หัวข้อ "รันยังไง")
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "study.db")

print("ฐานข้อมูลที่ใช้:", db_path)

conn = sqlite3.connect(db_path)

# ------------------------------------------------------------------
# หัวตาราง = ชื่อคอลัมน์ + ชนิดข้อมูล + constraint
#
# แต่ละบรรทัดข้างล่างอ่านได้ว่า  <ชื่อ>  <ชนิด>  <constraint>
#
#   id INTEGER PRIMARY KEY AUTOINCREMENT
#       PRIMARY KEY   = คอลัมน์ที่ใช้ชี้แถวนี้แถวเดียวในตาราง ห้ามซ้ำ ห้ามว่าง
#       AUTOINCREMENT = ไม่ต้องคิดเลขเอง SQLite นับให้ 1, 2, 3, ...
#                       และจะไม่เอาเลขของแถวที่ลบไปแล้วกลับมาใช้ซ้ำ
#
#   name TEXT NOT NULL
#       NOT NULL = ห้ามเว้นว่าง ถ้า INSERT โดยไม่ใส่ name จะ error ทันที
#                  ไม่ใช่ปล่อยให้มีแถวชื่อว่างค้างในตาราง
#
#   email TEXT NOT NULL UNIQUE
#       UNIQUE = ห้ามซ้ำกับแถวอื่น สมัครด้วยอีเมลเดิมสองครั้งไม่ได้
#                นี่คือการกันที่ "ระดับฐานข้อมูล" ซึ่งกันได้จริงกว่าเช็คใน Python
#                เพราะถ้าสองคนกดสมัครพร้อมกัน โค้ด Python อาจเช็คผ่านทั้งคู่
#
#   points INTEGER DEFAULT 0
#   accuracy REAL DEFAULT 0.0
#       DEFAULT = ถ้า INSERT ไม่ระบุค่ามา ให้ใช้ค่านี้แทน NULL
#                 ทำให้ไม่ต้องมานั่งเช็ค None ทุกครั้งที่อ่านออกมาคำนวณ
#
# เทียบกับตาราง Oyd ใน 00-basic-sqlite.py ที่เขียนแค่
#     Oyd(NAME TEXT, POINTS INTEGER, ACCURACY REAL)
# → ไม่มี PRIMARY KEY  = ไม่มีอะไรชี้ได้ว่า "แถวไหน" เวลาจะ UPDATE/DELETE
# → ไม่มี NOT NULL     = ใส่แถวเปล่าทั้งแถวก็ยังได้
# → ไม่มี UNIQUE       = ข้อมูลซ้ำสะสมโดยไม่มีใครเตือน
# นั่นคือเหตุผลที่ต้องคิดเรื่องหัวตารางตั้งแต่ตอนสร้าง ไม่ใช่ค่อยไปแก้ทีหลัง
# ------------------------------------------------------------------

# IF NOT EXISTS = รันซ้ำได้ไม่ error (ถ้าตารางมีอยู่แล้วก็ข้ามไป)
conn.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT    NOT NULL,
        email    TEXT    NOT NULL UNIQUE,
        points   INTEGER DEFAULT 0,
        accuracy REAL    DEFAULT 0.0
    );
    """
)

conn.commit()

# ------------------------------------------------------------------
# อ่านหัวตารางกลับมาดู — PRAGMA table_info คือสิ่งที่ DB Browser
# เอาไปแสดงในแท็บ Database Structure นั่นเอง
#
# แต่ละแถวที่ได้คือ (ลำดับ, ชื่อ, ชนิด, notnull, ค่า default, เป็น pk ไหม)
# ------------------------------------------------------------------
print("\nหัวตาราง users ที่ SQLite เก็บไว้จริง:")
print(f"{'#':<3} {'ชื่อคอลัมน์':<12} {'ชนิด':<9} {'NOT NULL':<9} {'DEFAULT':<9} {'PK'}")
print("-" * 60)

for cid, name, col_type, notnull, default, pk in conn.execute("PRAGMA table_info(users);"):
    print(
        f"{cid:<3} {name:<12} {col_type:<9} "
        f"{('ใช่' if notnull else '-'):<9} "
        f"{(str(default) if default is not None else '-'):<9} "
        f"{'ใช่' if pk else '-'}"
    )

# UNIQUE ไม่โผล่ใน table_info เพราะ SQLite เก็บเป็น index แยกต่างหาก
print("\nindex ที่เกิดจาก UNIQUE:")
for row in conn.execute("PRAGMA index_list(users);"):
    print("   ", row)

conn.close()

print("\nสร้างตารางเสร็จแล้ว — ขั้นต่อไป: python 02-insert-mock.py")
