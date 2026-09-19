# 03 — อ่านข้อมูล (SELECT)
#
# ตรงกับสไลด์ Read สองรูป ซึ่งสอนความต่างของ 2 คำสั่ง:
#     fetchone()  → เอาแถวเดียว   ได้ tuple หรือ None
#     fetchall()  → เอาทุกแถว     ได้ list ของ tuple (ถ้าไม่เจอได้ list ว่าง)
#
# แล้วต่อด้วย query ที่ต้องมีข้อมูลเยอะๆ ถึงจะเห็นผล (ORDER BY / GROUP BY)
#
# ไฟล์นี้ไม่แก้ข้อมูลอะไรเลย เลยไม่ต้อง commit()
#
# ต้องรัน 01 และ 02 มาก่อน

import os
import sqlite3

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "study.db")


# ==================================================================
# ส่วนที่ 1 — fetchone() แบบสไลด์เป๊ะ
# ==================================================================
def get_user(user_id):
    """อ่าน user คนเดียวตาม id — โครงเดียวกับในสไลด์"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = :id", {"id": user_id})
    user = cursor.fetchone()  # ไม่เจอ → คืน None (ไม่ใช่ error)
    conn.close()
    return user


print("=" * 62)
print("1) fetchone() — อ่านทีละคน")
print("=" * 62)

user_id = 1
user = get_user(user_id)

if user is None:
    # สไลด์ไม่ได้เช็คตรงนี้ พอ user เป็น None แล้วไปเรียก user[0] ต่อ
    # จะได้ TypeError: 'NoneType' object is not subscriptable
    # ซึ่งอ่านแล้วงงว่าพังเพราะอะไร ทั้งที่สาเหตุจริงคือ "ไม่มีแถวนี้"
    print(f"ไม่พบ user id = {user_id} (ถ้าเพิ่งรัน 04 มา ให้รัน 02 ใหม่)")
else:
    # เข้าถึงค่าด้วยเลข index แบบสไลด์: user[0] คือคอลัมน์แรก
    print(f"User ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, "
          f"Points: {user[3]}, Accuracy: {user[4]}")


# ------------------------------------------------------------------
# เวอร์ชันที่ดีกว่า — row_factory = sqlite3.Row
#
# ปัญหาของ user[1]: เลข index ผูกกับ "ลำดับคอลัมน์ในตาราง"
# วันไหนมีคนเพิ่มคอลัมน์แทรกกลางตาราง เลขทุกตัวหลังจากนั้นจะเลื่อน
# แล้วโค้ดจะไม่ error — มันจะ print ค่าผิดคอลัมน์ออกมาเงียบๆ ซึ่งหาเจอยากกว่ามาก
#
# sqlite3.Row ทำให้เรียกด้วยชื่อคอลัมน์ได้ user["name"] → คอลัมน์เลื่อนก็ยังถูก
# และถ้าพิมพ์ชื่อผิดจะ error ทันทีตรงจุดที่ผิด
# ------------------------------------------------------------------
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

row = cursor.execute("SELECT * FROM users WHERE id = :id", {"id": user_id}).fetchone()
if row is not None:
    print(f"(แบบ Row) ID: {row['id']}, Name: {row['name']}, Email: {row['email']}, "
          f"Points: {row['points']}, Accuracy: {row['accuracy']}")


# ==================================================================
# ส่วนที่ 2 — fetchall() แบบสไลด์
# ==================================================================
print("\n" + "=" * 62)
print("2) fetchall() — อ่านทุกคนที่ points > 80")
print("=" * 62)

cursor.execute("SELECT * FROM users WHERE points > :min_points", {"min_points": 80})
users = cursor.fetchall()

print(f"เจอ {len(users)} คน")
for u in users:
    print(f"  ID: {u['id']:<3} Name: {u['name']:<10} Points: {u['points']:<5} "
          f"Accuracy: {u['accuracy']}")


# ==================================================================
# ส่วนที่ 3 — query ที่ต้องมีข้อมูล 20 แถวถึงจะเห็นผล
# (ตรงกับตาราง "Query ที่จะต้องเขียน" ใน ../README.md)
# ==================================================================
print("\n" + "=" * 62)
print("3) ORDER BY + LIMIT — 5 อันดับคะแนนสูงสุด")
print("=" * 62)

# ORDER BY <คอลัมน์> DESC = เรียงมาก→น้อย (ASC คือน้อย→มาก ซึ่งเป็นค่าเริ่มต้น)
# LIMIT = ตัดเอาแค่กี่แถวแรก — ต้องมาคู่กับ ORDER BY เสมอ
#         เพราะถ้าไม่เรียงก่อน "5 แถวแรก" คือแถวไหนก็ได้ที่ SQLite หยิบมา
for rank, u in enumerate(
    cursor.execute("SELECT name, points FROM users ORDER BY points DESC LIMIT 5"),
    start=1,
):
    print(f"  {rank}. {u['name']:<10} {u['points']} แต้ม")


print("\n" + "=" * 62)
print("4) ฟังก์ชันรวม (aggregate) — สรุปทั้งตารางเหลือแถวเดียว")
print("=" * 62)

# COUNT / AVG / MAX / MIN ยุบหลายแถวให้เหลือค่าเดียว
# ROUND(..., 1) = ปัดทศนิยม 1 ตำแหน่ง ไม่งั้น AVG จะออกมายาวเป็นพรืด
# AS <ชื่อ> = ตั้งชื่อคอลัมน์ผลลัพธ์ ทำให้อ่านออกมาด้วยชื่อนั้นได้เลย
# ตั้งเป็นภาษาอังกฤษไว้เพราะ PostgreSQL (ปลายทางตาม ../README.md) เข้มเรื่อง
# ชื่อ identifier มากกว่า SQLite — เขียนให้ย้ายได้ตั้งแต่แรกดีกว่าไปแก้ทีหลัง
stat = cursor.execute(
    """
    SELECT COUNT(*)             AS n_users,
           ROUND(AVG(points), 1) AS avg_points,
           MAX(points)           AS max_points,
           MIN(points)           AS min_points
    FROM users
    """
).fetchone()

print(f"  จำนวนคน       : {stat['n_users']}")
print(f"  คะแนนเฉลี่ย   : {stat['avg_points']}")
print(f"  สูงสุด/ต่ำสุด : {stat['max_points']} / {stat['min_points']}")


print("\n" + "=" * 62)
print("5) GROUP BY + HAVING — แบ่งคนเป็นช่วงคะแนน")
print("=" * 62)

# CASE WHEN ... THEN ... END = if/elif/else ของ SQL ใช้สร้างคอลัมน์ใหม่จากค่าเดิม
# GROUP BY = ยุบแถวที่มีค่าคอลัมน์นั้นเหมือนกันให้เหลือแถวเดียวต่อกลุ่ม
#            แล้วฟังก์ชันรวม (COUNT/AVG) จะทำงาน "ต่อกลุ่ม" แทนที่จะทำทั้งตาราง
#
# HAVING ต่างจาก WHERE ตรงจังหวะที่กรอง:
#     WHERE  กรอง "แถวดิบ" ก่อนจัดกลุ่ม
#     HAVING กรอง "ผลลัพธ์ของกลุ่ม" หลังจัดกลุ่มแล้ว
# เขียน WHERE COUNT(*) >= 2 ไม่ได้ เพราะตอน WHERE ทำงาน ยังไม่มีกลุ่มให้นับ
for g in cursor.execute(
    """
    SELECT CASE
               WHEN points >= 150 THEN 'สูง   (150+)'
               WHEN points >= 80  THEN 'กลาง  (80-149)'
               ELSE                    'ต่ำ    (0-79)'
           END                     AS tier,
           COUNT(*)                AS n_users,
           ROUND(AVG(accuracy), 2) AS avg_accuracy
    FROM users
    GROUP BY tier
    HAVING COUNT(*) >= 2
    ORDER BY n_users DESC
    """
):
    print(f"  {g['tier']:<16} {g['n_users']:>2} คน   ความแม่นเฉลี่ย {g['avg_accuracy']}")

# หมายเหตุ: ความแม่นเฉลี่ยของกลุ่มที่มี John Doe (accuracy 95.5) จะเพี้ยนไปเลย
# เพราะค่านั้นคนละหน่วยกับคนอื่น — ดูคำอธิบายใน 02-insert-mock.py

conn.close()

print("\nขั้นต่อไป: python 04-update-delete.py")
