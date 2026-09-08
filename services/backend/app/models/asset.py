"""
Asset Model
ตาราง assets สำหรับเก็บ metadata ของรูปภาพที่ถูกสร้างขึ้น
"""

from datetime import datetime, timezone
from app.models import db


class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prompt = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self) -> dict:
        """แปลง Object เป็น Dictionary สำหรับตอบกลับเป็น JSON"""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "file_path": self.file_path,
            "image_url": f"/api/assets/{self.id}/image",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
