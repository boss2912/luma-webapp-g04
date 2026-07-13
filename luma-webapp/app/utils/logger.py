"""
app/utils/logger.py — Logging Configuration
--------------------------------------------
Input   : ชื่อ module ที่ต้องการ log
Process : สร้าง logger พร้อม format มาตรฐาน
Output  : Logger object

การใช้งาน:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("message")
    logger.error("error message")
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app=None):
    """
    ตั้งค่า logging สำหรับทั้งแอป
    เรียกครั้งเดียวใน create_app() ใน __init__.py
    """
    log_level = logging.DEBUG if (app and app.debug) else logging.INFO

    # Format: เวลา [ระดับ] ชื่อ module: ข้อความ
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # Console handler (แสดงใน terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    console_handler.setLevel(log_level)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # ลบ handler เดิมก่อน (ป้องกัน duplicate)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    # File handler (optional — เก็บ log ไว้อ่านทีหลัง)
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "luma.log"),
        maxBytes=1_000_000,   # 1 MB
        backupCount=3,
    )
    file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    file_handler.setLevel(logging.WARNING)  # เก็บเฉพาะ WARNING+ ใน file
    root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    สร้าง logger สำหรับ module ที่ระบุ
    ใช้ใน routes หรือ utils ต่าง ๆ
    """
    return logging.getLogger(name)
