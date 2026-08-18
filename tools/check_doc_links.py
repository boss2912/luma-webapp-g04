#!/usr/bin/env python3
"""
tools/check_doc_links.py
========================
ตรวจว่าลิงก์ในไฟล์ .md ทุกไฟล์ชี้ไปยังไฟล์/หัวข้อที่มีอยู่จริง

ทำไมต้องมี
----------
เอกสารของโปรเจกต์นี้อ้างถึงกันไปมาเยอะมาก (README -> docs -> services -> archive)
พอย้ายหรือเปลี่ยนชื่อไฟล์ทีเดียว ลิงก์จะตายเงียบๆ โดยไม่มีอะไรฟ้อง
GitHub ก็ไม่เตือน — คนอ่านจะเจอหน้า 404 เอาเอง

ตรวจอะไรบ้าง
------------
- ลิงก์แบบ [ข้อความ](path)              -> ไฟล์มีจริงไหม
- ลิงก์แบบ [ข้อความ](path#หัวข้อ)        -> ไฟล์มีจริง + หัวข้อนั้นมีจริงไหม
- ลิงก์แบบ [ข้อความ](#หัวข้อ)            -> หัวข้อในไฟล์เดียวกันมีจริงไหม
- ลิงก์แบบอ้างอิง [ข้อความ][ref] + [ref]: path
- รูป ![alt](path)
- <a href="path"> ใน HTML ที่ฝังใน markdown
- ลิงก์ภายนอก http(s):// -> ข้าม (ต้องต่อเน็ต ทำให้ CI ช้าและไม่เสถียร)
  ใช้ --external ถ้าอยากตรวจด้วย

การใช้งาน
---------
    python tools/check_doc_links.py
    python tools/check_doc_links.py --external     # ยิงเช็คลิงก์ภายนอกด้วย
    python tools/check_doc_links.py --skip archive # ข้ามโฟลเดอร์

exit code 0 = ผ่าน · 1 = มีลิงก์เสีย
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}

# [ข้อความ](target)  และ  ![alt](target)
INLINE_LINK = re.compile(r"!?\[(?P<text>[^\]]*)\]\((?P<target><[^>]*>|[^()\s]*(?:\([^()]*\)[^()\s]*)*)(?:\s+\"[^\"]*\")?\)")
# [ref]: target
REF_DEF = re.compile(r"^\s{0,3}\[(?P<id>[^\]]+)\]:\s*(?P<target>\S+)")
# [ข้อความ][ref]
REF_USE = re.compile(r"\[(?P<text>[^\]]*)\]\[(?P<id>[^\]]*)\]")
# <a href="...">
HTML_HREF = re.compile(r"<a\s[^>]*href=[\"'](?P<target>[^\"']+)[\"']", re.IGNORECASE)
# หัวข้อ markdown
HEADING = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.+?)\s*#*\s*$")
# บล็อกโค้ด — ลิงก์ข้างในไม่ใช่ลิงก์จริง
FENCE = re.compile(r"^\s{0,3}(```|~~~)")


def slugify(text: str) -> str:
    """แปลงหัวข้อเป็น anchor แบบเดียวกับที่ GitHub ทำ

    ทำตาม github-slugger ตามลำดับนี้เป๊ะ:
        lowercase -> trim -> ลบ HTML tag -> ลบเครื่องหมายวรรคตอน
        -> แทน "ช่องว่างแต่ละตัว" ด้วยขีด

    จุดที่พลาดกันบ่อย: GitHub **ไม่ยุบ** ช่องว่างซ้ำให้เหลือขีดเดียว
    หัวข้อ `## 3. วิธีที่ 1 — venv + pip (Windows)` ตัด `—` กับ `+` ออกแล้ว
    เหลือช่องว่างติดกันสองตัว anchor จริงจึงเป็น `3-วิธีที่-1--venv--pip-windows`
    (ขีดคู่) ไม่ใช่ขีดเดี่ยว — ถ้ายุบจะฟ้องผิดว่าลิงก์ที่ถูกอยู่แล้วเสีย

    ภาษาไทยถูกเก็บไว้ทั้งหมด เพราะ GitHub รองรับ unicode ใน anchor
    """
    # แยกส่วนที่อยู่ในเครื่องหมาย ` ออกก่อน แล้วค่อยล้าง markdown เฉพาะส่วนนอก
    #
    # เหตุผล: เนื้อในโค้ดเป็น "ข้อความจริง" ไม่ใช่ไวยากรณ์
    # หัวข้อ ``### `GET /api/assets/<id>/image` `` มี `<id>` เป็นตัวอักษรจริง
    # ถ้าล้าง HTML tag ทั้งบรรทัดจะไป กิน <id> ทิ้ง ได้ anchor เป็น
    # `get-apiassetsimage` แต่ของจริง GitHub ให้ `get-apiassetsidimage`
    # เพราะตัวเรนเดอร์ escape < > เป็นข้อความไปแล้วก่อนคำนวณ anchor
    parts = []
    for chunk in re.split(r"(`[^`]*`)", text):
        if len(chunk) >= 2 and chunk.startswith("`") and chunk.endswith("`"):
            parts.append(chunk[1:-1])                        # เนื้อในโค้ด เก็บดิบ
            continue
        chunk = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", chunk)   # [t](u)
        chunk = re.sub(r"[*~]", "", chunk)                         # **bold** ~del~
        chunk = re.sub(r"<[!/a-zA-Z][^>]*>", "", chunk)            # <span> </b>
        parts.append(chunk)
    text = unicodedata.normalize("NFC", "".join(parts)).strip().lower()

    # เก็บตัวอักษร/ตัวเลข, _ , - และช่องว่าง ที่เหลือทิ้ง
    #
    # ต้องเก็บ "เครื่องหมายประกอบ" (unicode category M) ไว้ด้วย
    # สระบนล่างและวรรณยุกต์ไทย เช่น ' ้ ' (U+0E49) เป็น category Mn
    # ซึ่ง str.isalnum() คืน False และ \w ของ Python ก็ไม่จับ
    # ถ้าใช้ \w เฉยๆ คำว่า "ด้วย" จะกลายเป็น "ดวย" ผิดจาก anchor จริงของ GitHub
    kept = []
    for ch in text:
        if ch in " \t":
            kept.append("-")
        elif ch.isalnum() or ch in "_-" or unicodedata.category(ch).startswith("M"):
            kept.append(ch)
    return "".join(kept)


def strip_code_blocks(lines: list[str]) -> list[tuple[int, str]]:
    """คืน (เลขบรรทัด, ข้อความดิบ) เฉพาะบรรทัดที่อยู่นอกบล็อกโค้ด ```...```

    คืนข้อความ "ดิบ" โดยไม่ลบ inline code ออก เพราะฟังก์ชันนี้ใช้สองงาน
    และสองงานต้องการคนละอย่าง:

      หาหัวข้อ  -> ต้องเก็บเนื้อใน `code` ไว้ เพราะ GitHub เอาไปทำ anchor ด้วย
                   หัวข้อ ``## ADR-007 ... ต้องใช้ `-r` `` มี `-r` อยู่ใน anchor จริง
      หาลิงก์   -> ต้องลบ inline code ทิ้ง เพราะ `[a](b)` ในเครื่องหมาย backtick
                   เป็นแค่ตัวอย่างที่เขียนให้อ่าน ไม่ใช่ลิงก์

    การลบ inline code จึงไปทำที่ collect_targets ซึ่งเป็นฝั่งที่ต้องการ
    """
    out: list[tuple[int, str]] = []
    fence: str | None = None
    for lineno, raw in enumerate(lines, start=1):
        match = FENCE.match(raw)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif raw.strip().startswith(fence):
                fence = None
            continue
        if fence is not None:
            continue
        out.append((lineno, raw))
    return out


def mask_inline_code(line: str) -> str:
    """แทน `...` ด้วยช่องว่าง — ใช้ตอนหาลิงก์เท่านั้น ไม่ใช้ตอนหาหัวข้อ"""
    return re.sub(r"`[^`]*`", "``", line)


def anchors_of(path: Path, cache: dict[Path, set[str]]) -> set[str]:
    """เก็บ anchor ทั้งหมดในไฟล์ .md (จากหัวข้อ + จาก id=/name= ที่เขียนเอง)"""
    if path in cache:
        return cache[path]
    found: set[str] = set()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        cache[path] = found
        return found

    seen: dict[str, int] = {}
    for _, line in strip_code_blocks(lines):
        match = HEADING.match(line)
        if match:
            slug = slugify(match.group("text"))
            if not slug:
                continue
            # หัวข้อชื่อซ้ำ GitHub ต่อท้ายด้วย -1, -2, ...
            count = seen.get(slug, 0)
            found.add(slug if count == 0 else f"{slug}-{count}")
            seen[slug] = count + 1
    for line in lines:
        for attr in re.findall(r"<[^>]*\s(?:id|name)=[\"']([^\"']+)[\"']", line):
            found.add(attr.lower())
    cache[path] = found
    return found


def collect_targets(md: Path) -> list[tuple[int, str, str]]:
    """คืน (บรรทัด, ประเภท, target) ของลิงก์ทั้งหมดในไฟล์"""
    lines = md.read_text(encoding="utf-8").splitlines()
    body = [(n, mask_inline_code(text)) for n, text in strip_code_blocks(lines)]

    definitions: dict[str, str] = {}
    results: list[tuple[int, str, str]] = []

    for lineno, line in body:
        ref = REF_DEF.match(line)
        if ref:
            definitions[ref.group("id").lower()] = ref.group("target")
            results.append((lineno, "ref-def", ref.group("target")))
            continue
        for match in INLINE_LINK.finditer(line):
            results.append((lineno, "inline", match.group("target").strip("<>")))
        for match in HTML_HREF.finditer(line):
            results.append((lineno, "html", match.group("target")))

    for lineno, line in body:
        for match in REF_USE.finditer(line):
            key = (match.group("id") or match.group("text")).lower()
            if key in definitions:
                continue
            results.append((lineno, "ref-missing", f"[{key}]"))

    return results


def check_file(md: Path, anchor_cache: dict[Path, set[str]],
               check_external: bool) -> list[tuple[int, str, str]]:
    """คืนรายการ (บรรทัด, target, เหตุผลที่เสีย)"""
    problems: list[tuple[int, str, str]] = []

    for lineno, kind, target in collect_targets(md):
        if kind == "ref-missing":
            problems.append((lineno, target, "ใช้ลิงก์แบบอ้างอิงแต่ไม่มีการนิยาม"))
            continue
        if not target:
            problems.append((lineno, "(ว่าง)", "target ว่าง"))
            continue

        parsed = urlparse(target)
        if parsed.scheme in ("http", "https"):
            if check_external:
                problems.extend(check_external_url(lineno, target))
            continue
        if parsed.scheme in ("mailto", "tel", "data"):
            continue

        raw_path, _, fragment = target.partition("#")
        raw_path = unquote(raw_path)
        fragment = unquote(fragment)

        if raw_path:
            resolved = (md.parent / raw_path).resolve()
            if not resolved.exists():
                rel = raw_path
                problems.append((lineno, target, f"ไม่พบไฟล์: {rel}"))
                continue
        else:
            resolved = md

        if fragment and resolved.suffix.lower() == ".md":
            wanted = slugify(unquote(fragment))
            available = anchors_of(resolved, anchor_cache)
            if wanted and wanted not in available:
                near = [a for a in available if wanted[:6] and wanted[:6] in a]
                hint = f" — ใกล้เคียง: {near[:3]}" if near else ""
                problems.append((lineno, target, f"ไม่พบหัวข้อ #{fragment}{hint}"))

    return problems


def check_external_url(lineno: int, url: str) -> list[tuple[int, str, str]]:
    import urllib.error                       # noqa: PLC0415 - ใช้เฉพาะโหมด --external
    import urllib.request                     # noqa: PLC0415

    request = urllib.request.Request(
        url, method="HEAD",
        headers={"User-Agent": "luma-doc-link-check/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status >= 400:
                return [(lineno, url, f"HTTP {response.status}")]
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 405, 999):
            # หลายเว็บบล็อก HEAD หรือ bot — ไม่ถือว่าลิงก์เสีย
            return []
        return [(lineno, url, f"HTTP {exc.code}")]
    except Exception as exc:                  # noqa: BLE001 - network อะไรก็เกิดได้
        return [(lineno, url, f"{type(exc).__name__}: {exc}")]
    return []


# ---------------------------------------------------------------------------
# self-test ของ slugify
#
# คู่ (หัวข้อ -> anchor) ทุกคู่ในนี้ "ไม่ได้เดา" — ดึงมาจาก id="user-content-..."
# ที่ github.com สร้างจริงบนหน้าเรนเดอร์ของ repo นี้ (ยืนยันเมื่อ 18 ส.ค. 2026
# ครบ 141/141 หัวข้อ จาก 6 ไฟล์)
#
# เก็บไว้เพราะกฎการทำ anchor ของ GitHub มีกับดักหลายชั้นที่เดาไม่ถูก
# ถ้าใครแก้ slugify แล้วเผลอทำพัง ชุดนี้จะฟ้องทันทีโดยไม่ต้องต่อเน็ต
# ---------------------------------------------------------------------------
SLUG_CASES: list[tuple[str, str]] = [
    # ช่องว่างซ้ำไม่ถูกยุบ — "—" หายไปแล้วเหลือช่องว่างสองตัว = ขีดสองตัว
    ("LUMA — Learning-based Universal Media Artist",
     "luma--learning-based-universal-media-artist"),
    ("🏗️ สถาปัตยกรรม — Distributed System 3 เครื่อง",
     "️-สถาปัตยกรรม--distributed-system-3-เครื่อง"),
    # emoji หายไป แต่ช่องว่างหลัง emoji ยังกลายเป็นขีดนำหน้า
    ("📌 สถานะปัจจุบัน", "-สถานะปัจจุบัน"),
    ("📚 เอกสารที่ต้องอ่าน", "-เอกสารที่ต้องอ่าน"),
    ("🎯 LUMA คืออะไร", "-luma-คืออะไร"),
    # วงเล็บถูกตัด ไม่เหลือขีดแทนที่
    ("👥 ทีม (3 คน)", "-ทีม-3-คน"),
    ("ติดตั้งเร็วสุด (dev บนเครื่องเดียว)", "ติดตั้งเร็วสุด-dev-บนเครื่องเดียว"),
    ("🎓 เกณฑ์ให้คะแนน (Lecture 1 หน้า 6)", "-เกณฑ์ให้คะแนน-lecture-1-หน้า-6"),
    # เนื้อในเครื่องหมาย ` เป็นข้อความจริง <id> ต้องไม่ถูกตัดทิ้งแบบ HTML tag
    ("`GET /api/assets/<id>/image`", "get-apiassetsidimage"),
    ("`POST /pipeline/<stage>/<operation>`", "post-pipelinestageoperation"),
    ("`DELETE /api/assets/<id>`", "delete-apiassetsid"),
    ("`POST /api/generate` — สร้างภาพ", "post-apigenerate--สร้างภาพ"),
    # สระและวรรณยุกต์ไทย (unicode category Mn) ต้องไม่หาย
    ("3. วิธีที่ 1 — venv + pip (Windows)", "3-วิธีที่-1--venv--pip-windows"),
    ("Frontend → Backend", "frontend--backend"),
]


def run_self_test() -> int:
    print("=" * 62)
    print("  self-test: slugify ตรงกับ anchor จริงของ GitHub")
    print("=" * 62)
    bad = 0
    for heading, expected in SLUG_CASES:
        got = slugify(heading)
        ok = got == expected
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {heading[:44]}")
        if not ok:
            print(f"         คาดว่า : {expected}")
            print(f"         ได้    : {got}")
    print()
    print("=" * 62)
    if bad:
        print(f"ไม่ผ่าน {bad}/{len(SLUG_CASES)}")
        print("=" * 62)
        return 1
    print(f"ผ่าน {len(SLUG_CASES)}/{len(SLUG_CASES)}")
    print("=" * 62)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ตรวจว่าลิงก์ในไฟล์ .md ชี้ไปยังไฟล์/หัวข้อที่มีอยู่จริง")
    parser.add_argument("--self-test", action="store_true",
                        help="ทดสอบว่า slugify ยังตรงกับกฎ anchor ของ GitHub")
    parser.add_argument("--external", action="store_true",
                        help="ตรวจลิงก์ http(s) ด้วย (ต้องต่อเน็ต ช้ากว่ามาก)")
    parser.add_argument("--skip", action="append", default=[],
                        help="ข้ามโฟลเดอร์ (ใส่ซ้ำได้)")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    skip = SKIP_DIRS | set(args.skip)
    md_files = sorted(
        p for p in REPO_ROOT.rglob("*.md")
        if not (skip & set(p.relative_to(REPO_ROOT).parts))
    )

    print("=" * 62)
    print(f"  ตรวจลิงก์ในเอกสาร ({len(md_files)} ไฟล์"
          f"{', รวมลิงก์ภายนอก' if args.external else ''})")
    print("=" * 62)

    anchor_cache: dict[Path, set[str]] = {}
    total_links = 0
    total_bad = 0

    for md in md_files:
        rel = md.relative_to(REPO_ROOT).as_posix()
        links = collect_targets(md)
        total_links += len(links)
        problems = check_file(md, anchor_cache, args.external)
        if not problems:
            print(f"[OK]   {rel}  ({len(links)} ลิงก์)")
            continue
        total_bad += len(problems)
        print(f"[FAIL] {rel}")
        for lineno, target, why in problems:
            print(f"          บรรทัด {lineno}: {target}")
            print(f"            -> {why}")

    print()
    print("=" * 62)
    if total_bad:
        print(f"ไม่ผ่าน: ลิงก์เสีย {total_bad} จุด จากทั้งหมด {total_links} ลิงก์")
        print("=" * 62)
        return 1
    print(f"ผ่าน: ลิงก์ทั้งหมด {total_links} ลิงก์ ใน {len(md_files)} ไฟล์ ชี้ถูกทุกอัน")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
