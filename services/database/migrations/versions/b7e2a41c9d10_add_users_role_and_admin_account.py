"""เพิ่ม users.role และสร้างบัญชี admin ตั้งต้น

Revision ID: b7e2a41c9d10
Revises: f369fc41b5c7
Create Date: 2026-10-12 21:00:00.000000

ทำ 2 อย่าง
    1. เพิ่มคอลัมน์ role ให้ตาราง users — แถวเดิมทุกแถวได้ค่า "user"
    2. สร้างบัญชี admin ตั้งต้น (ชื่อ admin) เพื่อให้มีคนเข้าหน้าจัดการผู้ใช้ได้
       ตั้งแต่ติดตั้งเสร็จ

รหัสผ่านตั้งต้นเขียนไว้ในไฟล์นี้ตรงๆ
    เป็นการตัดสินใจของเจ้าของงาน (12 ต.ค. 2569): ระบบนี้ใช้ส่งวิชาอย่างเดียว
    ไม่มีผู้ใช้จริง ถ้าเอาไปใช้จริงต้องเปลี่ยนรหัสนี้ในหน้า admin ทันที
    เพราะ repo นี้เป็น public ใครก็อ่านค่านี้ได้

ถ้ามีคนสมัครชื่อ admin ไว้ก่อนแล้ว
    migration ไม่สร้างแถวซ้ำ (ชื่อซ้ำไม่ได้) และไม่แตะรหัสผ่านของบัญชีนั้น
    แค่ยกบัญชีนั้นขึ้นเป็น role admin

ทำไมใช้ op.add_column / op.drop_column ตรงๆ ไม่ใช้ batch_alter_table
    batch mode ของ SQLite สร้างตาราง users ใหม่แล้วลบของเดิม ซึ่งถ้า foreign key
    เปิดอยู่จะลบ assets ของผู้ใช้ตามไปด้วย (ดูคำอธิบายใน c1a7f5d9e204)
    ALTER TABLE ... ADD COLUMN / DROP COLUMN ไม่สร้างตารางใหม่ จึงไม่มีความเสี่ยงนี้
"""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa
from werkzeug.security import generate_password_hash


# revision identifiers, used by Alembic.
revision = 'b7e2a41c9d10'
down_revision = 'f369fc41b5c7'
branch_labels = None
depends_on = None

ADMIN_NAME = "admin"
ADMIN_EMAIL = "admin@luma.local"
ADMIN_INITIAL = "admin1234"


def upgrade():
    # 1. เพิ่มคอลัมน์ — server_default ทำให้แถวเดิมทุกแถวได้ "user" ทันที
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
    )

    # 2. หาว่ามีบัญชีชื่อ admin หรืออีเมลนี้อยู่แล้วไหม
    conn = op.get_bind()
    existing_id = conn.execute(
        sa.text("SELECT id FROM users WHERE username = :name OR email = :email"),
        {"name": ADMIN_NAME, "email": ADMIN_EMAIL},
    ).scalar()

    if existing_id is None:
        # ยังไม่มี -> สร้างใหม่ เก็บรหัสเป็น hash เหมือนบัญชีที่สมัครผ่านหน้าเว็บ
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            sa.text(
                "INSERT INTO users (username, email, password_hash, role, created_at) "
                "VALUES (:name, :email, :password_hash, 'admin', :now)"
            ),
            {
                "name": ADMIN_NAME,
                "email": ADMIN_EMAIL,
                "password_hash": generate_password_hash(ADMIN_INITIAL),
                "now": now,
            },
        )
    else:
        # มีอยู่แล้ว -> ยกขึ้นเป็น admin โดยไม่แตะรหัสผ่านเดิม
        conn.execute(
            sa.text("UPDATE users SET role = 'admin' WHERE id = :id"),
            {"id": existing_id},
        )


def downgrade():
    """ถอดคอลัมน์ role ออก — ไม่ลบบัญชี admin เพราะการลบ user จะลบ assets ของเขาตาม"""
    op.drop_column("users", "role")
