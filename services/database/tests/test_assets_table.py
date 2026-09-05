"""พิสูจน์เงื่อนไข MUST ของ issue #45 (Walking Skeleton) ฝั่งฐานข้อมูล

#45 เขียนเงื่อนไขไว้เป็นภาษาคน 2 ข้อ ไฟล์นี้แปลเป็นข้อพิสูจน์:

    "กดปุ่ม 3 ครั้งได้ 3 ภาพ ไม่ทับกัน"  ->  INSERT 3 แถวโดยไม่ใส่ id
                                              ต้องได้ id = 1, 2, 3 เอง
    "กด F5 แล้วภาพเดิมยังอยู่"           ->  ปิดการเชื่อมต่อแล้วเปิดใหม่
                                              ข้อมูลยังอยู่ และเรียงใหม่->เก่าถูก

ทดสอบบนไฟล์ .db ชั่วคราวของ pytest เสมอ ไม่แตะ instance/luma.db ของจริง
และสร้างตารางด้วย migration จริง ไม่ใช่ db.create_all() (ADR-008 กฎข้อ 2)
"""

import os
import sqlite3
import sys
from datetime import timedelta
from pathlib import Path

import pytest
from flask_migrate import upgrade

# services/database/ — ที่อยู่ของ migrate_app.py
DATABASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DATABASE_DIR))


@pytest.fixture()
def app(tmp_path):
    """app ที่ชี้ไปยังไฟล์ .db ชั่วคราว และรัน migration ครบทุกตัวแล้ว"""
    db_file = tmp_path / "test_assets.db"

    # migrate_app อ่าน env ตัวนี้ตอนเรียก create_migration_app() ไม่ใช่ตอน import
    # จึงตั้งค่าแล้วเรียกฟังก์ชันเองได้เลย ไม่ต้อง reload module
    os.environ["LUMA_DATABASE_URI"] = "sqlite:///" + str(db_file).replace("\\", "/")

    from migrate_app import create_migration_app

    application = create_migration_app()

    with application.app_context():
        # สร้างตารางด้วยเส้นทางเดียวกับตอน deploy จริง
        # ถ้า migration พัง test จะล้มตรงนี้ ซึ่งเป็นสิ่งที่ต้องการ
        upgrade()

    application.config["_DB_FILE"] = str(db_file)
    yield application

    os.environ.pop("LUMA_DATABASE_URI", None)


def test_insert_3_rows_gets_id_1_2_3(app):
    """MUST ข้อ 1 — กดปุ่ม 3 ครั้งได้ 3 ภาพ ไม่ทับกัน

    ไม่ใส่ id ตอน INSERT เลย ปล่อยให้ SQLite เดินเลขเอง
    (คอลัมน์ INTEGER PRIMARY KEY เป็น alias ของ rowid จึงเดินเลขให้อัตโนมัติ)
    """
    from app.models import Asset, db

    with app.app_context():
        for i in range(1, 4):
            db.session.add(Asset(prompt=f"ภาพที่ {i}", file_path=f"generated/{i}.png"))
        db.session.commit()

        ids = [row.id for row in Asset.query.order_by(Asset.id).all()]

    assert ids == [1, 2, 3], f"id ต้องเดินเอง 1-2-3 แต่ได้ {ids}"


def test_rows_survive_reconnect_and_sort_newest_first(app):
    """MUST ข้อ 2 — กด F5 แล้วภาพเดิมยังอยู่ และเรียงใหม่->เก่าถูก

    "ปิดโปรแกรมแล้วเปิดใหม่" จำลองด้วยการปิด session ของ SQLAlchemy
    แล้วเปิดไฟล์เดิมด้วย sqlite3 ตรงๆ ซึ่งเป็นคนละ connection กันจริง
    ถ้าข้อมูลค้างอยู่แค่ในหน่วยความจำ ขั้นนี้จะไม่เจออะไรเลย

    created_at กำหนดเองให้ห่างกันชัดเจน เพราะ 3 แถวที่เขียนติดกันใน
    เสี้ยววินาทีเดียวอาจได้เวลาเท่ากัน แล้วจะพิสูจน์การเรียงไม่ได้
    """
    from app.models import Asset, db
    from app.models.asset import utcnow

    base = utcnow().replace(tzinfo=None)

    with app.app_context():
        db.session.add_all(
            [
                Asset(prompt="เก่าสุด", file_path="a.png", created_at=base),
                Asset(prompt="กลาง", file_path="b.png", created_at=base + timedelta(minutes=1)),
                Asset(prompt="ใหม่สุด", file_path="c.png", created_at=base + timedelta(minutes=2)),
            ]
        )
        db.session.commit()
        db.session.remove()  # ตัดการเชื่อมต่อของ SQLAlchemy ทิ้ง

    # เปิดไฟล์เดิมใหม่ด้วย connection คนละตัว — ตรงกับที่ผู้ใช้กด F5
    con = sqlite3.connect(app.config["_DB_FILE"])
    try:
        rows = con.execute(
            "SELECT prompt FROM assets ORDER BY created_at DESC"
        ).fetchall()
    finally:
        con.close()

    assert len(rows) == 3, f"ข้อมูลต้องอยู่ครบ 3 แถวหลังเปิดใหม่ แต่เหลือ {len(rows)}"
    assert [r[0] for r in rows] == ["ใหม่สุด", "กลาง", "เก่าสุด"]


def test_prompt_and_file_path_are_required(app):
    """คอลัมน์ที่ประกาศ NOT NULL ต้องกันได้จริงที่ระดับฐานข้อมูล

    ไม่ใช่แค่ NOT NULL ในโมเดล — ถ้า migration ไม่ได้ใส่ NOT NULL ลงตารางจริง
    แถวที่ไม่มี prompt จะหลุดเข้าไปได้ แล้ว Asset Hub ค้นด้วย ?q= ไม่เจอตลอดไป
    """
    from app.models import Asset, db
    from sqlalchemy.exc import IntegrityError

    with app.app_context():
        db.session.add(Asset(file_path="no_prompt.png"))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
