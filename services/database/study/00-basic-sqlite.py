# # python code to create a relation
# # using SQLite3

# # import the sqlite3 package
# import sqlite3

# # create a database named backup
# cnt = sqlite3.connect("backup.db")

# # create a table named Boss
# cnt.execute('''CREATE TABLE Oyd(NAME TEXT, POINTS INTEGER, ACCURACY REAL);''')

# cnt.commit()

# cnt.close()

import sqlite3
import os

# จุดสำคัญ: หาตำแหน่งโฟลเดอร์ของไฟล์ .py นี้เอง (ไม่สนใจว่าจะรันจากที่ไหน)
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "backup.db")

print("จะสร้าง/เปิดไฟล์ที่:", db_path)

cnt = sqlite3.connect(db_path)  # ใช้ path เต็ม แทน "backup.db" เฉยๆ
cnt.execute('''CREATE TABLE IF NOT EXISTS Oyd(
NAME TEXT,
POINTS INTEGER,
ACCURACY REAL);''')
cnt.commit()
cnt.close()

print("เสร็จแล้ว! เปิดไฟล์นี้ใน DB Browser ได้เลย:", db_path)