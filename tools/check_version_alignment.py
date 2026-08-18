#!/usr/bin/env python3
"""
tools/check_version_alignment.py
================================
ตรวจว่า package ที่ปรากฏในหลาย service ถูกล็อกเป็น "เวอร์ชันเดียวกัน"

ทำไมต้องมี (ADR-001 ใน docs/DECISIONS.md)
------------------------------------------
โปรเจกต์นี้มี requirements 3 ไฟล์ (backend / ai-engine / database)
บางตัวอยู่ในหลายไฟล์ เช่น Pillow, requests, pytest

ตอน deploy จริงแยก 3 เครื่อง เวอร์ชันไม่ตรงกันก็ไม่พัง
แต่ตอน dev ทุกคนลงรวมใน venv เดียวด้วย requirements-dev.txt
ถ้าไฟล์หนึ่งขอ Pillow==11.0 อีกไฟล์ขอ Pillow==12.3
pip จะติดตั้งตัวสุดท้ายที่เจอ แล้วเงียบ — เครื่องแต่ละคนได้ไม่เหมือนกัน
กลายเป็นบั๊ก "เครื่องผมรันได้" ที่หาสาเหตุยากที่สุด

v1 เป็นแบบนี้จริง ตอน v2 จึงจัดให้ตรงกันหมด และให้สคริปต์นี้เฝ้าไว้

ตรวจอะไรบ้าง
------------
1. package ที่อยู่หลายไฟล์ ต้อง pin เวอร์ชันเดียวกัน
2. ทุกบรรทัดต้อง pin ด้วย `==` ไม่ใช่ `>=` หรือปล่อยว่าง
   (>= แปลว่าอีก 3 เดือนคนที่ลงใหม่จะได้คนละเวอร์ชันกับที่ทดสอบไว้)
3. requirements-dev.txt ต้องอ้างไฟล์ของทุก service ด้วย `-r`
   ไม่ใช่ copy รายการมาวาง (copy แล้วจะลืมอัปเดต)
4. environment.yml (Conda) ต้องมี pip package ตรงกับ requirements
5. ไม่มี package ซ้ำภายในไฟล์เดียวกัน

การใช้งาน
---------
    python tools/check_version_alignment.py

exit code 0 = ผ่าน · 1 = ไม่ตรงกัน
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SERVICE_REQS = [
    Path("services/backend/requirements.txt"),
    Path("services/ai-engine/requirements.txt"),
    Path("services/database/requirements.txt"),
]
DEV_REQ = Path("requirements-dev.txt")
CONDA_ENV = Path("environment.yml")

# ชื่อ package บน PyPI ไม่สนตัวพิมพ์ใหญ่เล็ก และ - กับ _ ถือว่าเหมือนกัน (PEP 503)
def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


PIN = re.compile(
    r"^(?P<name>[A-Za-z0-9._-]+)"
    r"(?P<extras>\[[^\]]*\])?"
    r"\s*(?P<op>==|>=|<=|~=|!=|>|<)?\s*"
    r"(?P<version>[^\s;#]+)?"
    r"(?P<marker>\s*;.*)?$"
)


def parse_requirements(path: Path) -> tuple[dict[str, str], list[str], list[str]]:
    """คืน (package -> เวอร์ชัน, บรรทัด -r ที่อ้างไฟล์อื่น, ปัญหาที่เจอ)"""
    pins: dict[str, str] = {}
    includes: list[str] = []
    problems: list[str] = []
    seen: dict[str, int] = {}

    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith(("-r ", "--requirement ")):
            includes.append(line.split(None, 1)[1].strip())
            continue
        if line.startswith("-"):        # -e, --index-url ฯลฯ ไม่ใช่ pin
            continue

        match = PIN.match(line)
        if not match:
            problems.append(f"บรรทัด {lineno}: อ่านไม่ออก -> {line!r}")
            continue

        name = normalize(match.group("name"))
        op = match.group("op")
        version = match.group("version")

        if op != "==" or not version:
            problems.append(
                f"บรรทัด {lineno}: {match.group('name')} ไม่ได้ล็อกด้วย == "
                f"(เจอ {line!r}) — คนที่ลงทีหลังจะได้คนละเวอร์ชัน")
            continue

        if name in seen:
            problems.append(
                f"บรรทัด {lineno}: {match.group('name')} ซ้ำกับบรรทัด {seen[name]}")
        seen[name] = lineno
        pins[name] = version

    return pins, includes, problems


def parse_conda(path: Path) -> dict[str, str]:
    """ดึงเฉพาะ package ใต้บล็อก `- pip:` ของ environment.yml

    อ่านแบบง่ายด้วย regex ไม่ใช้ PyYAML เพราะไม่อยากให้เครื่องมือ dev
    ต้องลง dependency เพิ่ม แค่จะรันตัวตรวจ
    """
    pins: dict[str, str] = {}
    in_pip = False
    pip_indent = 0

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())

        if re.match(r"^\s*-\s*pip\s*:\s*$", line):
            in_pip = True
            pip_indent = indent
            continue
        if in_pip and indent <= pip_indent and not line.lstrip().startswith("-"):
            in_pip = False
        if not in_pip:
            continue

        match = re.match(r"^\s*-\s*([A-Za-z0-9._-]+)\s*==\s*([^\s;]+)\s*$", line)
        if match:
            pins[normalize(match.group(1))] = match.group(2)
    return pins


def main() -> int:
    print("=" * 66)
    print("  ตรวจความสอดคล้องของเวอร์ชัน dependency (ADR-001)")
    print("=" * 66)

    errors: list[str] = []
    all_pins: dict[Path, dict[str, str]] = {}

    # ---- 1. อ่าน requirements ของแต่ละ service ----------------------------
    for rel in SERVICE_REQS:
        path = REPO_ROOT / rel
        if not path.exists():
            errors.append(f"ไม่พบไฟล์ {rel.as_posix()}")
            continue
        pins, _, problems = parse_requirements(path)
        all_pins[rel] = pins
        status = "OK" if not problems else "FAIL"
        print(f"[{status:4}] {rel.as_posix():45} {len(pins)} package")
        for problem in problems:
            errors.append(f"{rel.as_posix()}: {problem}")

    # ---- 2. package ที่อยู่หลายไฟล์ ต้องเวอร์ชันตรงกัน ---------------------
    print()
    print("  package ที่ใช้ร่วมกันหลาย service")
    print("  " + "-" * 62)

    everywhere: dict[str, dict[str, str]] = {}
    for rel, pins in all_pins.items():
        for name, version in pins.items():
            everywhere.setdefault(name, {})[rel.as_posix()] = version

    shared = {n: v for n, v in everywhere.items() if len(v) > 1}
    if not shared:
        print("  (ไม่มี package ที่ซ้ำข้าม service)")
    for name in sorted(shared):
        versions = shared[name]
        distinct = set(versions.values())
        if len(distinct) == 1:
            where = ", ".join(Path(p).parts[1] for p in sorted(versions))
            print(f"  [OK]   {name:22} {next(iter(distinct)):12} ({where})")
        else:
            print(f"  [FAIL] {name:22} เวอร์ชันไม่ตรงกัน")
            for source in sorted(versions):
                print(f"           {versions[source]:12} <- {source}")
            errors.append(
                f"{name}: pin ไม่ตรงกัน {sorted(distinct)} — "
                f"คนที่ลงใน venv เดียวจะได้ไม่เหมือนกัน")

    # ---- 3. requirements-dev.txt ต้องใช้ -r ไม่ใช่ copy รายการ -------------
    print()
    dev_path = REPO_ROOT / DEV_REQ
    if not dev_path.exists():
        errors.append(f"ไม่พบ {DEV_REQ.as_posix()}")
    else:
        dev_pins, includes, dev_problems = parse_requirements(dev_path)
        errors.extend(f"{DEV_REQ.as_posix()}: {p}" for p in dev_problems)
        included = {normalize_path(i) for i in includes}
        missing = [r.as_posix() for r in SERVICE_REQS
                   if normalize_path(r.as_posix()) not in included]
        if missing:
            errors.append(
                f"{DEV_REQ.as_posix()} ไม่ได้ -r ไฟล์เหล่านี้: {missing}")
            print(f"[FAIL] {DEV_REQ.as_posix()} ขาด -r: {missing}")
        else:
            print(f"[OK  ] {DEV_REQ.as_posix():45} -r ครบ {len(includes)} ไฟล์")
        if dev_pins:
            errors.append(
                f"{DEV_REQ.as_posix()} pin เวอร์ชันเองด้วย ({sorted(dev_pins)}) "
                f"— ควรใช้ -r อย่างเดียว ไม่งั้นจะลืมอัปเดตสองที่")

    # ---- 4. environment.yml ต้องตรงกับ requirements -----------------------
    conda_path = REPO_ROOT / CONDA_ENV
    if not conda_path.exists():
        errors.append(f"ไม่พบ {CONDA_ENV.as_posix()}")
    else:
        conda_pins = parse_conda(conda_path)
        union: dict[str, str] = {}
        for pins in all_pins.values():
            union.update(pins)

        mismatched = {n: (v, union[n]) for n, v in conda_pins.items()
                      if n in union and v != union[n]}
        missing_in_conda = sorted(set(union) - set(conda_pins))
        extra_in_conda = sorted(set(conda_pins) - set(union))

        if mismatched or missing_in_conda:
            print(f"[FAIL] {CONDA_ENV.as_posix():45} {len(conda_pins)} pip package")
            for name, (conda_version, req_version) in sorted(mismatched.items()):
                print(f"          {name}: conda {conda_version} != "
                      f"requirements {req_version}")
                errors.append(
                    f"{CONDA_ENV.as_posix()}: {name} = {conda_version} "
                    f"แต่ requirements = {req_version}")
            if missing_in_conda:
                print(f"          ขาดใน conda: {missing_in_conda}")
                errors.append(
                    f"{CONDA_ENV.as_posix()} ขาด: {missing_in_conda} — "
                    f"คนใช้ Conda จะได้ env ไม่ครบ")
        else:
            print(f"[OK  ] {CONDA_ENV.as_posix():45} "
                  f"{len(conda_pins)} pip package ตรงกับ requirements")
        if extra_in_conda:
            print(f"          (หมายเหตุ: มีเฉพาะใน conda: {extra_in_conda})")

    # ---- สรุป -------------------------------------------------------------
    print()
    print("=" * 66)
    if errors:
        print(f"ไม่ผ่าน: พบ {len(errors)} ปัญหา")
        for error in errors:
            print(f"  - {error}")
        print()
        print("อ่านเหตุผลได้ที่ docs/DECISIONS.md -> ADR-001")
        print("=" * 66)
        return 1

    total = len({n for pins in all_pins.values() for n in pins})
    print(f"ผ่าน: {total} package ล็อกด้วย == ครบ และเวอร์ชันตรงกันทุกไฟล์")
    print("=" * 66)
    return 0


def normalize_path(text: str) -> str:
    return text.replace("\\", "/").lstrip("./").lower()


if __name__ == "__main__":
    sys.exit(main())
