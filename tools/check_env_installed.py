#!/usr/bin/env python3
"""
tools/check_env_installed.py
============================
ตรวจว่า "environment ที่กำลังใช้อยู่จริง" ตรงกับที่ repo ล็อกไว้หรือไม่

ต่างจาก check_version_alignment.py ตรงไหน
-----------------------------------------
    check_version_alignment.py   ตรวจว่า *ไฟล์* สอดคล้องกันเอง
    ตัวนี้                        ตรวจว่า *ของที่ลงในเครื่อง* ตรงกับไฟล์

สองอย่างนี้ผ่าน/ไม่ผ่านแยกกันได้ และช่องว่างระหว่างมันเคยเกิดขึ้นจริง:
env conda ชื่อ luma ของสมาชิกคนหนึ่งเป็น Python 3.11 + Flask 3.1.3
ทั้งที่ repo ล็อก Python 3.12 + Flask 3.0.3 — ไม่ตรง 11 จาก 16 ตัว
โดยที่ check_version_alignment.py รายงาน "ผ่าน" อยู่ตลอด เพราะไฟล์ตรงกันจริง

นี่คือต้นทางของบั๊ก "เครื่องผมรันได้ เครื่องคุณไม่ได้" ที่ ADR-001 พูดถึง
ADR-001 ปิดฝั่งไฟล์ไว้แล้ว สคริปต์นี้ปิดฝั่งเครื่อง

ตรวจอะไรบ้าง
------------
1. เวอร์ชัน Python ตรงกับ python= ใน environment.yml
2. package ที่ repo ล็อกไว้ ลงครบไหม
3. ที่ลงแล้ว เวอร์ชันตรงไหม
4. (แจ้งเฉยๆ ไม่นับว่าผิด) package ที่ลงเกินมาจากที่ระบุ

การใช้งาน
---------
    python tools/check_env_installed.py                  # ครบทุก service
    python tools/check_env_installed.py --profile backend
    python tools/check_env_installed.py --profile ai-engine
    python tools/check_env_installed.py --profile database
    python tools/check_env_installed.py --show-extra
    python tools/check_env_installed.py --self-test

profile มีไว้สำหรับการ deploy แบบ 3 เครื่อง (Lecture 4 หน้า 56)
ที่แต่ละเครื่องลงเฉพาะของตัวเอง — เครื่อง backend ไม่ต้องมี OpenCV
ถ้าไม่ระบุ จะเทียบกับทุก service รวมกัน (เท่ากับ requirements-dev.txt)

exit code 0 = ผ่าน · 1 = ไม่ตรง
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from importlib import metadata
from pathlib import Path

# --- console encoding ------------------------------------------------------
# Windows Thai locale ใช้ codepage cp874 ซึ่งเข้ารหัส emoji ไม่ได้
# ทำให้ print() โยน UnicodeEncodeError แล้วสคริปต์ตายทั้งที่ตรวจผ่าน
# (เคยทำให้ pre-commit hook บล็อก commit มาแล้ว) — บังคับ UTF-8 ไว้เสมอ
def _force_utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


_force_utf8_stdout()

# ใช้ parser ตัวเดียวกับ check_version_alignment.py แทนที่จะเขียนซ้ำ
# ถ้ารูปแบบ requirements เปลี่ยน จะได้แก้ที่เดียว
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_version_alignment import (  # noqa: E402
    CONDA_ENV,
    REPO_ROOT,
    normalize,
    parse_conda,
    parse_requirements,
)

PROFILES = {
    "backend": [Path("services/backend/requirements.txt")],
    "ai-engine": [Path("services/ai-engine/requirements.txt")],
    "database": [Path("services/database/requirements.txt")],
    "dev": [
        Path("services/backend/requirements.txt"),
        Path("services/ai-engine/requirements.txt"),
        Path("services/database/requirements.txt"),
    ],
}

# package ที่ติดมากับ environment ตามปกติ ไม่ใช่ของที่เราเลือกลงเอง
# มีเกินมาไม่ถือว่าผิด จึงไม่ต้องรกหน้าจอตอน --show-extra
BASELINE = {
    "pip", "setuptools", "wheel", "packaging", "certifi", "charset-normalizer",
    "idna", "urllib3", "colorama", "typing-extensions", "greenlet", "mako",
    "markupsafe", "jinja2", "werkzeug", "click", "itsdangerous", "blinker",
}

OK, MISMATCH, MISSING = "ok", "mismatch", "missing"


def installed_packages() -> dict[str, str]:
    """ชื่อ package (normalize แล้ว) -> เวอร์ชันที่ลงจริงใน interpreter นี้"""
    found: dict[str, str] = {}
    for dist in metadata.distributions():
        try:
            name = dist.metadata["Name"]
        except Exception:      # metadata เสียหาย ข้ามไป ไม่ควรทำให้ตัวตรวจตาย
            continue
        if not name:
            continue
        found[normalize(name)] = dist.version
    return found


def compare(expected: dict[str, str],
            actual: dict[str, str]) -> dict[str, tuple[str, str, str | None]]:
    """เทียบสิ่งที่ควรมีกับสิ่งที่มีจริง

    คืน package -> (สถานะ, เวอร์ชันที่ควรเป็น, เวอร์ชันที่เจอ)
    ชื่อ package เทียบแบบ PEP 503 คือ - _ . ถือว่าเหมือนกัน และไม่สนตัวพิมพ์
    """
    normalized_actual = {normalize(n): v for n, v in actual.items()}
    result: dict[str, tuple[str, str, str | None]] = {}
    for name, want in expected.items():
        got = normalized_actual.get(normalize(name))
        if got is None:
            result[name] = (MISSING, want, None)
        elif got == want:
            result[name] = (OK, want, got)
        else:
            result[name] = (MISMATCH, want, got)
    return result


def expected_python(path: Path) -> str | None:
    """ดึงเวอร์ชัน Python จากบรรทัด `- python=3.12` ใน environment.yml"""
    if not path.exists():
        return None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        match = re.match(r"^-\s*python\s*=\s*([0-9][0-9.]*)\s*$", line)
        if match:
            return match.group(1)
    return None


def env_label() -> str:
    """บอกว่ากำลังตรวจ environment ไหน คนอ่านจะได้รู้ว่าตรวจถูกตัวหรือเปล่า"""
    conda = os.environ.get("CONDA_DEFAULT_ENV")
    if conda:
        return "conda env " + conda
    venv = os.environ.get("VIRTUAL_ENV")
    if venv:
        return "venv " + Path(venv).name
    # เรียก python ของ venv ตรงๆ โดยไม่ activate จะไม่มี VIRTUAL_ENV
    # แต่ยังบอกได้จาก sys.prefix ที่ต่างจาก base_prefix
    if sys.prefix != sys.base_prefix:
        return "venv " + Path(sys.prefix).name + " (ยังไม่ได้ activate)"
    return "Python ของระบบ (ไม่ได้อยู่ใน environment ไหนเลย)"


def fix_hint(profile: str) -> list[str]:
    """คำสั่งแก้ ให้ตรงกับเครื่องมือที่คนนั้นใช้อยู่จริง"""
    conda = os.environ.get("CONDA_DEFAULT_ENV")
    if conda:
        return [
            "environment นี้เป็น Conda — conda env update --prune",
            "ลดเวอร์ชัน Python ไม่ได้ ต้องสร้างใหม่:",
            "",
            "    conda deactivate",
            "    conda env remove -n " + conda,
            "    conda env create -f environment.yml",
            "    conda activate " + conda,
        ]
    if profile == "dev":
        return ["    pip install -r requirements-dev.txt"]
    return ["    pip install -r services/" + profile + "/requirements.txt"]


def run_check(profile: str, show_extra: bool) -> int:
    files = PROFILES[profile]

    print("=" * 66)
    print("  ตรวจว่า environment ที่ใช้อยู่ตรงกับที่ repo ล็อกไว้ไหม")
    print("=" * 66)
    print("  interpreter : " + sys.executable)
    print("  environment : " + env_label())
    print("  profile     : " + profile
          + "  (" + ", ".join(f.as_posix() for f in files) + ")")
    print()

    errors: list[str] = []

    # ---- 1. เวอร์ชัน Python ------------------------------------------------
    want_py = expected_python(REPO_ROOT / CONDA_ENV)
    got_py = ".".join(str(n) for n in sys.version_info[:2])
    if want_py is None:
        print("[--  ] Python " + got_py
              + " (environment.yml ไม่ได้ระบุไว้ ข้ามการตรวจ)")
    elif got_py == want_py:
        print("[OK  ] Python " + got_py)
    else:
        print("[FAIL] Python — ควรเป็น " + want_py + " แต่เจอ " + got_py)
        errors.append(
            "Python " + got_py + " ไม่ตรงกับ " + want_py
            + " ที่ environment.yml ระบุ — เวอร์ชัน Python ต่างกัน"
            + "ทำให้ behaviour ต่างกันได้ ไม่ใช่แค่เรื่อง package")

    # ---- 2. รวม package ที่ควรมี -------------------------------------------
    expected: dict[str, str] = {}
    for rel in files:
        path = REPO_ROOT / rel
        if not path.exists():
            errors.append("ไม่พบไฟล์ " + rel.as_posix())
            continue
        pins, _, problems = parse_requirements(path)
        if problems:
            # ปัญหาในตัวไฟล์เองเป็นหน้าที่ของ check_version_alignment.py
            print("[--  ] " + rel.as_posix() + " มีปัญหาในไฟล์เอง "
                  + str(len(problems)) + " จุด -> รัน check_version_alignment.py")
        expected.update(pins)

    if not expected:
        print("ไม่มี package ให้ตรวจ")
        return 1 if errors else 0

    # ---- 3. เทียบกับของจริง -------------------------------------------------
    actual = installed_packages()
    result = compare(expected, actual)

    good = sorted(n for n, (s, _, _) in result.items() if s == OK)
    bad = sorted(n for n, (s, _, _) in result.items() if s == MISMATCH)
    gone = sorted(n for n, (s, _, _) in result.items() if s == MISSING)

    print()
    print("  package ที่ต้องมี " + str(len(expected)) + " ตัว")
    print("  " + "-" * 62)
    for name in good:
        print("  [OK]   " + name.ljust(24) + result[name][1])
    for name in bad:
        _, want, got = result[name]
        print("  [ผิด]  " + name.ljust(24) + "ควรเป็น " + want.ljust(14)
              + "แต่เจอ " + str(got))
    for name in gone:
        print("  [ขาด]  " + name.ljust(24) + "ควรเป็น "
              + result[name][1].ljust(14) + "แต่ยังไม่ได้ลง")

    if bad:
        errors.append("เวอร์ชันไม่ตรง " + str(len(bad)) + " ตัว: " + ", ".join(bad))
    if gone:
        errors.append("ยังไม่ได้ลง " + str(len(gone)) + " ตัว: " + ", ".join(gone))

    # ---- 4. ของที่เกินมา (แจ้งเฉยๆ ไม่ทำให้ตก) ------------------------------
    if show_extra:
        known = {normalize(n) for n in expected} | {normalize(n) for n in BASELINE}
        extra = sorted(n for n in actual if n not in known)
        if extra:
            print()
            print("  หมายเหตุ: มี package อีก " + str(len(extra))
                  + " ตัวที่ไม่ได้อยู่ใน requirements (ไม่ถือว่าผิด)")
            for name in extra[:20]:
                print("    - " + name + " " + actual[name])
            if len(extra) > 20:
                print("    ... และอีก " + str(len(extra) - 20) + " ตัว")

    # ---- สรุป ---------------------------------------------------------------
    print()
    print("=" * 66)
    if errors:
        print("ไม่ผ่าน: พบ " + str(len(errors)) + " ปัญหา")
        for error in errors:
            print("  - " + error)
        print()
        print("วิธีแก้:")
        for line in fix_hint(profile):
            print("  " + line)
        print()
        print("อ่านเหตุผลได้ที่ docs/DECISIONS.md -> ADR-001 · INSTALL.md")
        print("=" * 66)
        return 1

    print("ผ่าน: Python " + got_py + " และ package ครบ " + str(len(good))
          + " ตัว ตรงกับที่ล็อกไว้")
    print("=" * 66)
    return 0


# ---------------------------------------------------------------------------
# self-test — ตรวจว่าตัวเปรียบเทียบยังจำแนกถูก โดยไม่ต้องพึ่ง env จริง
# ---------------------------------------------------------------------------
CASES: list[tuple[str, dict[str, str], dict[str, str], dict[str, str]]] = [
    ("ตรงกันหมด",
     {"flask": "3.0.3"}, {"flask": "3.0.3"}, {"flask": OK}),
    ("เวอร์ชันไม่ตรง",
     {"flask": "3.0.3"}, {"flask": "3.1.3"}, {"flask": MISMATCH}),
    ("ยังไม่ได้ลง",
     {"numpy": "2.5.2"}, {}, {"numpy": MISSING}),
    ("ชื่อที่ใช้ - กับ _ ต้องถือว่าตัวเดียวกัน (PEP 503)",
     {"Flask-SQLAlchemy": "3.1.1"}, {"flask_sqlalchemy": "3.1.1"},
     {"Flask-SQLAlchemy": OK}),
    ("ตัวพิมพ์ใหญ่เล็กไม่สำคัญ",
     {"SQLAlchemy": "2.0.52"}, {"sqlalchemy": "2.0.52"}, {"SQLAlchemy": OK}),
    ("จุดในชื่อก็ normalize (zope.interface = zope-interface)",
     {"zope.interface": "7.0"}, {"zope-interface": "7.0"},
     {"zope.interface": OK}),
    ("ต่างแค่เลข patch ก็ถือว่าไม่ตรง",
     {"sqlalchemy": "2.0.52"}, {"sqlalchemy": "2.0.51"},
     {"sqlalchemy": MISMATCH}),
    ("ของเกินมาไม่ทำให้ตก",
     {"flask": "3.0.3"}, {"flask": "3.0.3", "rich": "13.0"}, {"flask": OK}),
    ("ขาดกับผิดปนกันในรอบเดียว",
     {"flask": "3.0.3", "numpy": "2.5.2", "pytest": "9.1.1"},
     {"flask": "3.1.3", "pytest": "9.1.1"},
     {"flask": MISMATCH, "numpy": MISSING, "pytest": OK}),
]


def run_self_test() -> int:
    print("=" * 66)
    print("  self-test: การจำแนกสถานะ package")
    print("=" * 66)

    failed = 0
    for label, expected, actual, want in CASES:
        got = {n: s for n, (s, _, _) in compare(expected, actual).items()}
        if got == want:
            print("  [PASS] " + label)
        else:
            failed += 1
            print("  [FAIL] " + label)
            print("         ควรได้ " + str(want))
            print("         แต่ได้ " + str(got))

    # environment.yml จริงต้องอ่านเวอร์ชัน Python ออก ไม่งั้นข้อ 1 จะเงียบไปเฉยๆ
    want_py = expected_python(REPO_ROOT / CONDA_ENV)
    if want_py:
        print("  [PASS] อ่าน python=" + want_py + " จาก environment.yml ได้")
    else:
        failed += 1
        print("  [FAIL] อ่านเวอร์ชัน Python จาก environment.yml ไม่ได้")

    # และ pip section ต้องยังอ่านออก (กันกรณี environment.yml เปลี่ยนรูปแบบ)
    conda_pins = parse_conda(REPO_ROOT / CONDA_ENV)
    if conda_pins:
        print("  [PASS] อ่าน pip package จาก environment.yml ได้ "
              + str(len(conda_pins)) + " ตัว")
    else:
        failed += 1
        print("  [FAIL] อ่าน pip package จาก environment.yml ไม่ได้")

    total = len(CASES) + 2
    print()
    print("=" * 66)
    print("ผ่าน " + str(total - failed) + "/" + str(total))
    print("=" * 66)
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ตรวจว่า environment ที่ใช้อยู่ตรงกับที่ repo ล็อกไว้ไหม")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="dev",
                        help="ตรวจเฉพาะ service เดียว (สำหรับ deploy 3 เครื่อง)")
    parser.add_argument("--show-extra", action="store_true",
                        help="โชว์ package ที่ลงเกินมาจาก requirements ด้วย")
    parser.add_argument("--self-test", action="store_true",
                        help="ตรวจว่าตัวสคริปต์เองยังทำงานถูก")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_check(args.profile, args.show_extra)


if __name__ == "__main__":
    sys.exit(main())
