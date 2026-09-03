"""
โมเดล SQLAlchemy ของ LUMA
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.asset import Asset  # noqa: E402

__all__ = ["db", "Asset"]
