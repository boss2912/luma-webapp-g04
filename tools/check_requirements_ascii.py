#!/usr/bin/env python3
"""
tools/check_requirements_ascii.py
=================================
ตรวจว่าไฟล์ requirements*.txt ทุกไฟล์เป็น ASCII ล้วน

ทำไมต้องตรวจ
------------
pip อ่านไฟล์ requirements ด้วย codec ของ locale เครื่อง ไม่ใช่ UTF-8
บน Windows ภาษาไทย locale คือ cp874 ถ้าไฟล์เป็น UTF-8 ที่มีตัวอักษรไทย
`pip install -r` จะพังด้วย:

    UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 887
    decoding with 'cp874' codec failed

นี่คือปัญหาจริงที่โปรเจกต์นี้เจอใน v1 (ดู archive/ARCHITECTURE_v1.md ปัญหา B)
คำอธิบายภาษาไทยให้ไปอยู่ใน INSTALL.md แทน

การใช้งาน
---------
    python tools/check_requirements_ascii.py

exit code 0 = ผ่าน · 1 = พบตัวอักษรที่ไม่ใช่ ASCII

ใช้เป็น pre-commit hook ได้:
    python tools/check_requirements_ascii.py || exit 1
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def find_requirement_files() -> list[Path]:
    """หาไฟล์ requirements*.txt ทั้ง repo (ข้าม venv และ .git)"""
    skip_parts = {".git", ".venv", "venv", "env", "node_modules", "__pycache__"}
    found = []
    for path in REPO_ROOT.rglob("requirements*.txt"):
        if skip_parts & set(path.parts):
            continue
        found.append(path)
    return sorted(found)


def check_file(path: Path) -> list[tuple[int, int, str]]:
    """คืนรายการ (บรรทัด, คอลัมน์, ตัวอักษร) ที่ไม่ใช่ ASCII"""
    problems = []
    # อ่านเป็น utf-8 เพื่อให้เห็นตัวอักษรจริง แล้วค่อยเช็คว่า encode ascii ได้ไหม
    text = path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), start=1):
        for col, ch in enumerate(line, start=1):
            if ord(ch) > 127:
                problems.append((lineno, col, ch))
    return problems


def main() -> int:
    files = find_requirement_files()
    if not files:
        print("ไม่พบไฟล์ requirements*.txt เลย")
        return 0

    total_bad = 0
    for path in files:
        rel = path.relative_to(REPO_ROOT).as_posix()
        try:
            problems = check_file(path)
        except UnicodeDecodeError as exc:
            print(f"[ERROR] {rel} : อ่านเป็น UTF-8 ไม่ได้ -> {exc}")
            total_bad += 1
            continue

        if not problems:
            print(f"[OK]    {rel}")
            continue

        total_bad += 1
        # แสดงไม่เกิน 10 จุดแรก กันล้นจอ
        shown = problems[:10]
        print(f"[FAIL]  {rel} : พบตัวอักษรที่ไม่ใช่ ASCII {len(problems)} จุด")
        for lineno, col, ch in shown:
            print(f"          บรรทัด {lineno} คอลัมน์ {col}: {ch!r} (U+{ord(ch):04X})")
        if len(problems) > len(shown):
            print(f"          ... และอีก {len(problems) - len(shown)} จุด")

    print()
    if total_bad:
        print("=" * 62)
        print(f"ไม่ผ่าน: {total_bad} ไฟล์มีตัวอักษรที่ไม่ใช่ ASCII")
        print("แก้โดยเอาข้อความไทยออกจาก requirements แล้วย้ายไปไว้ใน INSTALL.md")
        print("=" * 62)
        return 1

    print("=" * 62)
    print(f"ผ่าน: requirements ทั้ง {len(files)} ไฟล์เป็น ASCII ล้วน")
    print("pip install -r จะทำงานได้บนเครื่อง locale ไทยโดยไม่ต้องตั้ง PYTHONUTF8")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
