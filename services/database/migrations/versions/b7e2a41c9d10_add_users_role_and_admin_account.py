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

ถ้ามีบัญชีชื่อ admin หรืออีเมล admin@luma.local อยู่ก่อนแล้ว
    ยกเป็น admin ต่อให้เฉพาะบัญชีตั้งต้นของระบบเอง (ชื่อ + อีเมลตรง และรหัสยังเป็นรหัสตั้งต้น)
    ซึ่งเกิดตอน downgrade แล้ว upgrade ซ้ำ — downgrade ไม่ลบแถวนี้
    นอกนั้น migration หยุดโดยไม่แก้อะไรเลย เพราะเป็นบัญชีที่ใครก็สมัครได้ (หน้าสมัครไม่กันชื่อ admin)
    ถ้ายกให้อัตโนมัติ คนที่สมัครชื่อ Admin ไว้ก่อนจะได้สิทธิ์ admin ด้วยรหัสของตัวเอง (#228 รีวิว)
    ผู้ดูแลต้องเปลี่ยนชื่อ/อีเมลของบัญชีนั้นก่อน แล้วรัน upgrade ใหม่
    บัญชีตั้งต้นที่รหัสยังเป็นรหัสตั้งต้นยกให้ได้ เพราะรหัสนั้นเปิดเผยใน repo อยู่แล้ว
    ใครก็ล็อกอินบัญชีนั้นได้เหมือนกัน การยกให้จึงไม่เพิ่มสิทธิ์ให้ใคร

ทำไมใช้ op.add_column / op.drop_column ตรงๆ ไม่ใช้ batch_alter_table
    batch mode ของ SQLite สร้างตาราง users ใหม่แล้วลบของเดิม ซึ่งถ้า foreign key
    เปิดอยู่จะลบ assets ของผู้ใช้ตามไปด้วย (ดูคำอธิบายใน c1a7f5d9e204)
    ALTER TABLE ... ADD COLUMN / DROP COLUMN ไม่สร้างตารางใหม่ จึงไม่มีความเสี่ยงนี้
"""
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa
from werkzeug.security import check_password_hash, generate_password_hash


# revision identifiers, used by Alembic.
revision = 'b7e2a41c9d10'
down_revision = 'f369fc41b5c7'
branch_labels = None
depends_on = None

ADMIN_NAME = "admin"
ADMIN_EMAIL = "admin@luma.local"
ADMIN_INITIAL = "admin1234"


def _is_bootstrap_admin(rows):
    """แถวที่ชนมีแถวเดียว และเป็นบัญชีตั้งต้นของระบบที่ยังไม่ได้เปลี่ยนรหัส"""
    if len(rows) != 1:
        return False
    row = rows[0]
    return (
        row.username.lower() == ADMIN_NAME
        and row.email == ADMIN_EMAIL
        and bool(row.password_hash)
        and check_password_hash(row.password_hash, ADMIN_INITIAL)
    )


def upgrade():
    # 1. หาว่ามีบัญชีชื่อ admin หรืออีเมลนี้อยู่แล้วไหม — ตรวจก่อนแก้อะไรทั้งนั้น
    #    SQLite ไม่ย้อน ALTER TABLE ให้ ถ้าหยุดหลังเพิ่มคอลัมน์ ฐานจะค้างครึ่งทาง upgrade ซ้ำไม่ได้
    #    (username เป็น COLLATE NOCASE จึงเจอ "Admin" ด้วย)
    conn = op.get_bind()
    existing = conn.execute(
        sa.text("SELECT id, username, email, password_hash FROM users WHERE username = :name OR email = :email"),
        {"name": ADMIN_NAME, "email": ADMIN_EMAIL},
    ).fetchall()
    if existing and not _is_bootstrap_admin(existing):
        raise RuntimeError(
            f"มีบัญชีชื่อ {ADMIN_NAME} หรืออีเมล {ADMIN_EMAIL} อยู่แล้ว และไม่ใช่บัญชีตั้งต้นของระบบ "
            "ไม่ยกเป็น admin ให้อัตโนมัติ — เปลี่ยนชื่อและอีเมลของบัญชีนั้นก่อน แล้วรัน upgrade ใหม่ / "
            f"An account named {ADMIN_NAME} or with email {ADMIN_EMAIL} already exists and is not the "
            "bootstrap account. Rename it, then run the upgrade again."
        )
    existing_id = existing[0].id if existing else None

    # 2. เพิ่มคอลัมน์ — server_default ทำให้แถวเดิมทุกแถวได้ "user" ทันที
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
    )

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
        # บัญชีตั้งต้นของระบบเอง (ผ่านเช็คข้อ 1 แล้ว) -> ยกกลับเป็น admin
        conn.execute(
            sa.text("UPDATE users SET role = 'admin' WHERE id = :id"),
            {"id": existing_id},
        )


def downgrade():
    """ถอดคอลัมน์ role ออก — ไม่ลบบัญชี admin เพราะการลบ user จะลบ assets ของเขาตาม"""
    op.drop_column("users", "role")
