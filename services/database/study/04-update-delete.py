# 04 — แก้ไข (UPDATE) และลบ (DELETE)
#
# ตรงกับสไลด์ Update และ Delete
#
# ทั้งสองคำสั่งมีจุดร่วมที่อันตรายเหมือนกันคือ WHERE
#     ลืม WHERE ตอน UPDATE = ทับค่าทุกแถวในตาราง
#     ลืม WHERE ตอน DELETE = ล้างตารางทั้งตาราง
# และ SQLite ไม่ถามยืนยัน ไม่มี undo — commit ไปแล้วคือจบ
#
# ต้องรัน 01 และ 02 มาก่อน

import os
import sqlite3

script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "study.db")


def show(user_id, label):
    """print แถวเดียวไว้เทียบก่อน/หลัง"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM users WHERE id = :id", {"id": user_id}).fetchone()
    conn.close()
    if row is None:
        print(f"  {label:<6}: (ไม่มีแถว id = {user_id} แล้ว)")
    else:
        print(f"  {label:<6}: name={row['name']:<12} email={row['email']:<24} "
              f"points={row['points']:<5} accuracy={row['accuracy']}")


# ==================================================================
# UPDATE
# ==================================================================
def update_user(user_id, name=None, email=None, points=None, accuracy=None):
    """
    แก้เฉพาะฟิลด์ที่ส่งมา — โจทย์เดียวกับสไลด์ แต่ยิง SQL ครั้งเดียว

    สไลด์เขียนเป็น if 4 ก้อน แต่ละก้อนยิง UPDATE ของตัวเอง:
        if name:  cursor.execute('UPDATE users SET name = ? WHERE id = ?', ...)
        if email: cursor.execute('UPDATE users SET email = ? WHERE id = ?', ...)
        ...
    ซึ่งอ่านง่ายดี แต่ถ้าส่งมาครบ 4 ฟิลด์ = ยิง 4 คำสั่ง แก้แถวเดียวกัน 4 รอบ
    และถ้าคำสั่งที่ 3 พังกลางทาง คำสั่งที่ 1-2 แก้ไปแล้ว → ข้อมูลค้างครึ่งๆ กลางๆ

    ข้างล่างประกอบ SET ท่อนเดียวแล้วยิงครั้งเดียว
    """
    # ⚠️ จุดสำคัญ: ที่ประกอบเป็นสตริงได้ตรงนี้คือ "ชื่อคอลัมน์" เท่านั้น
    #    และชื่อคอลัมน์มาจาก key ของ dict ที่เราเขียนเองในโค้ด (ไม่ได้มาจากผู้ใช้)
    #    ส่วน "ค่า" ยังผูกด้วย named parameter :name :email ... เหมือนเดิมทุกตัว
    #    → ค่าจากผู้ใช้ไม่มีทางกลายเป็นคำสั่ง SQL
    fields = {
        "name": name,
        "email": email,
        "points": points,
        "accuracy": accuracy,
    }

    # ทำไมต้อง "is not None" ไม่ใช่ if value:
    #     ถ้าเขียน if points: แล้วส่ง points=0 มา → 0 เป็น falsy จะโดนข้าม
    #     กลายเป็นว่าตั้งคะแนนเป็น 0 ไม่ได้เลย
    #     สไลด์เจอปัญหานี้เหมือนกัน เลยต้องเขียน if name: กับ if points is not None:
    #     ต่างกัน ซึ่งสับสน — ใช้ is not None ให้เหมือนกันหมดดีกว่า
    to_update = {k: v for k, v in fields.items() if v is not None}

    if not to_update:
        print("  ไม่มีอะไรให้แก้ — ข้าม")
        return 0

    set_clause = ", ".join(f"{col} = :{col}" for col in to_update)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        # WHERE id = :id ห้ามลืม ไม่งั้นทับทั้งตาราง
        f"UPDATE users SET {set_clause} WHERE id = :id",
        {**to_update, "id": user_id},
    )
    changed = cursor.rowcount  # จำนวนแถวที่โดนแก้จริง — 0 แปลว่าไม่เจอ id นั้น
    conn.commit()              # ไม่ commit = พอ close() การแก้จะหายไปเฉยๆ
    conn.close()
    return changed


print("=" * 62)
print("UPDATE — แก้ points กับ accuracy ของ id = 2")
print("=" * 62)

show(2, "ก่อน")
n = update_user(2, points=10, accuracy=0.55)   # สไลด์เรียก update_user(1, points=10, accuracy=10.5)
print(f"  แก้ไป {n} แถว")
show(2, "หลัง")

print("\n  ลอง id ที่ไม่มีอยู่จริง (id = 9999):")
n = update_user(9999, points=1)
# ไม่ error แต่ rowcount = 0 — UPDATE ที่ไม่เจอแถวไม่ถือว่าผิดพลาดในสายตา SQL
# ถ้าโค้ดจริงต้องรู้ว่า "แก้ไม่โดน" ต้องเช็ค rowcount เอง
print(f"  แก้ไป {n} แถว  <- ไม่ error แต่ไม่โดนอะไรเลย ต้องเช็ค rowcount เอง")


# ==================================================================
# DELETE
# ==================================================================
def delete_user(user_id):
    """ลบ user ตาม id — โครงเดียวกับสไลด์เป๊ะ"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = :id", {"id": user_id})
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted


print("\n" + "=" * 62)
print("DELETE — ลบทีละแถวด้วย WHERE")
print("=" * 62)

conn = sqlite3.connect(db_path)
before = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

# สไลด์เรียก delete_user(1) คือลบ Alice ทิ้งเลย
# ที่นี่ไม่ทำแบบนั้น เพราะจะทำให้ 03-read.py (ซึ่งอ่าน id = 1) พังตอนรันซ้ำ
# และ AUTOINCREMENT จะไม่เอาเลข 1 กลับมาใช้ ต่อให้รัน 02 ใหม่ Alice ก็ได้ id ใหม่
# → สร้างแถวชั่วคราวขึ้นมาลบแทน คำสั่ง DELETE ที่ใช้เหมือนสไลด์ทุกตัวอักษร
conn.execute(
    "INSERT OR IGNORE INTO users (name, email, points) VALUES (:name, :email, :points)",
    {"name": "Temp", "email": "temp@example.com", "points": 1},
)
conn.commit()
temp_id = conn.execute(
    "SELECT id FROM users WHERE email = :email", {"email": "temp@example.com"}
).fetchone()[0]
conn.close()

print(f"  ก่อนลบ : {before + 1} แถว (รวมแถวชั่วคราว id = {temp_id})")
n = delete_user(temp_id)
print(f"  ลบไป   : {n} แถว")

conn = sqlite3.connect(db_path)
after = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
conn.close()
print(f"  หลังลบ : {after} แถว")

# ------------------------------------------------------------------
# ⛔ อย่าเผลอเขียน
#        DELETE FROM users;
#    ไม่มี WHERE = ลบทุกแถวในตาราง ไม่มีคำถามยืนยัน ไม่มี undo
#
# นิสัยที่ช่วยได้: เขียน SELECT ก่อนเสมอ
#        SELECT * FROM users WHERE id = 5;   ← ดูก่อนว่าโดนแถวไหนบ้าง
#        DELETE FROM users WHERE id = 5;     ← ค่อยเปลี่ยน SELECT * เป็น DELETE
# ------------------------------------------------------------------

print("\nขั้นต่อไป: python 05-assets-luma.py — เอาแพตเทิร์นนี้ไปใช้กับตารางจริงของ LUMA")
