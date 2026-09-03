"""
ตาราง assets — ภาพที่ระบบสร้างขึ้น 1 แถวต่อ 1 ภาพ
"""

from datetime import datetime, timezone

from app.models import db


def utcnow() -> datetime:
    """เวลาปัจจุบันเป็น UTC"""
    return datetime.now(timezone.utc)


class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow, index=True)

    def __repr__(self) -> str:
        head = (self.prompt or "")[:40]
        return f"<Asset {self.id} {head!r}>"

    def to_dict(self) -> dict:
        """แปลงเป็น dict ตามรูปแบบใน docs/API_CONTRACT.md"""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "tags": [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "image_url": f"/api/assets/{self.id}/image",
        }
