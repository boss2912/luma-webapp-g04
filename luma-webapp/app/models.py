"""
Database Models
----------------
Input   : ข้อมูล user สมัคร / รูปที่ generate / งานที่ยิงไป Forge AI
Process : กำหนดตาราง SQL ผ่าน SQLAlchemy ORM
Output  : ตาราง users, assets, jobs ใน SQLite/PostgreSQL
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assets = db.relationship("Asset", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Asset(db.Model):
    """เก็บรูปที่ user generate/edit ไว้ใน Asset Hub (ตามสไลด์ Smart Canvas / Asset Hub)"""
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    prompt = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(255), nullable=True)  # เช่น "portrait,anime,4k"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Job(db.Model):
    """เก็บสถานะงานที่ยิงไป Forge AI (queue / pending / done / failed)"""
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, running, done, failed
    result_asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    # User.query.get() ถูก deprecated ใน SQLAlchemy 2.x → ใช้ db.session.get() แทน
    return db.session.get(User, int(user_id))
