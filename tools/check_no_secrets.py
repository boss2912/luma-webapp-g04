#!/usr/bin/env python3
"""
tools/check_no_secrets.py
=========================
กันไม่ให้ secret / ฐานข้อมูล / ข้อมูลส่วนตัว หลุดขึ้น git

ทำไมต้องมี
----------
1. v1 เคย commit `SECRET_KEY` ขึ้น GitHub จริง (archive/SECURITY_FIXES_v1.md F09)
2. v1 เคย commit `instance/luma.db` ทำให้ test ล้ม 3 ข้อ เพราะ schema ในไฟล์เก่า
   ไม่ตรงกับ models และ `db.create_all()` ไม่ ALTER ตารางเดิม
3. repo นี้เป็น public — ชื่อจริง ชื่อเล่น อีเมล รหัสนักศึกษา และ path
   `C:\\Users\\<ชื่อ>\\...` ไม่ควรหลุดออกไป

.gitignore ช่วยได้เฉพาะไฟล์ที่ยัง untracked — ถ้าเผลอ `git add -f`
หรือไฟล์ถูก track ไปแล้วก่อนเพิ่มกฎ .gitignore จะไม่ช่วยอะไรเลย
ตัวนี้ตรวจ "สิ่งที่กำลังจะ commit จริง" จึงดักได้อีกชั้น

การใช้งาน
---------
    python tools/check_no_secrets.py              # ตรวจไฟล์ที่ staged (pre-commit)
    python tools/check_no_secrets.py --all        # ตรวจไฟล์ที่ track ทั้ง repo
    python tools/check_no_secrets.py --staged     # เท่ากับไม่ใส่อะไร

exit code 0 = ผ่าน · 1 = พบของที่ไม่ควรขึ้น git

รายชื่อส่วนตัวของแต่ละคน
------------------------
อย่าเขียนชื่อจริงลงในสคริปต์นี้ (สคริปต์อยู่บน repo public — เท่ากับหลุดเอง)
ให้สร้างไฟล์ `tools/personal_terms.local.txt` ในเครื่องตัวเอง บรรทัดละ 1 คำ
ไฟล์นี้อยู่ใน .gitignore แล้ว จะไม่ถูก commit

    # tools/personal_terms.local.txt
    ชื่อเล่นของฉัน
    my.email@example.com
    6712345678
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCAL_TERMS_FILE = REPO_ROOT / "tools" / "personal_terms.local.txt"

# ไฟล์ที่ยกเว้นการตรวจ "เนื้อหา" เพราะตัวมันเองต้องเขียน pattern พวกนี้
CONTENT_SCAN_EXEMPT = {
    "tools/check_no_secrets.py",
    "tools/README.md",
    ".gitignore",
}

# ---------------------------------------------------------------------------
# กฎที่ 1 - ชื่อไฟล์ที่ห้ามขึ้น git เด็ดขาด
# ---------------------------------------------------------------------------
FORBIDDEN_PATHS: list[tuple[str, str]] = [
    (r"(^|/)instance/config\.py$",
     "ไฟล์ config จริงของเครื่อง — commit ได้แค่ config.py.example"),
    (r"(^|/)\.env$|(^|/)\.env\.(?!example)",
     "ไฟล์ .env จริง — commit ได้แค่ .env.example"),
    (r"\.(db|sqlite|sqlite3|db-journal|db-wal|db-shm)$",
     "ไฟล์ฐานข้อมูล — v1 เคย commit แล้วทำ test ล้ม เพราะ schema ค้างเก่า"),
    (r"\.(safetensors|ckpt|pt|pth)$",
     "ไฟล์ model AI ใหญ่หลาย GB — อยู่บนเครื่อง AI Server เท่านั้น"),
    (r"(^|/)id_rsa$|(^|/)id_ed25519$|\.pem$|\.key$|\.pfx$|\.p12$",
     "private key / certificate"),
    (r"(^|/)\.pypirc$|(^|/)\.netrc$|(^|/)\.npmrc$",
     "ไฟล์ credential ของเครื่องมือ"),
    (r"(^|/)(venv|\.venv)/",
     "โฟลเดอร์ virtual environment — ห้ามขึ้น git ให้ใช้ requirements.txt แทน"),
]

# ---------------------------------------------------------------------------
# กฎที่ 2 - เนื้อหาที่บ่งชี้ว่ามี secret
# แต่ละข้อ: (ชื่อกฎ, regex, คำอธิบาย)
# ---------------------------------------------------------------------------
SECRET_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("assigned-secret",
     # SECRET_KEY = "อะไรก็ตามยาว >= 8" แต่ยอมให้ค่าที่ชี้ไป env / placeholder
     re.compile(
         r"""(?ix)
         \b(secret_key|password|passwd|api_key|apikey|access_token|
            auth_token|private_key|client_secret|db_password)\b
         \s*[:=]\s*
         ['"]([^'"\n]{8,})['"]
         """),
     "ค่า secret เขียนตรงๆ ในโค้ด — ย้ายไป instance/config.py หรือ env var"),

    ("private-key-block",
     re.compile(r"-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
     "private key ฝังอยู่ในไฟล์"),

    ("aws-key",
     re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
     "AWS access key id"),

    ("github-token",
     re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
     "GitHub personal access token"),

    ("slack-token",
     re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
     "Slack token"),

    ("db-url-with-password",
     re.compile(r"(?i)\b(postgres|postgresql|mysql|mongodb)(\+\w+)?://"
                r"[^:\s/]+:(?P<pw>[^@\s/]+)@"),
     "connection string ที่มีรหัสผ่านอยู่ข้างใน"),
]

# ---------------------------------------------------------------------------
# แยก "ค่าตัวอย่าง" ออกจาก "secret จริง"
#
# ทำแบบรายชื่อ placeholder อย่างเดียวไม่พอ — พอเจอคำใหม่ก็ต้องมาไล่เติมเรื่อยๆ
# จึงใช้สองชั้น:
#   ชั้น 1  ตรงกับรูปแบบ placeholder ที่รู้จัก           -> ไม่ใช่ secret
#   ชั้น 2  "หน้าตาสุ่ม" ไหม (entropy สูง คละชนิดอักขระ) -> ถึงจะถือว่าเป็น secret
# ค่าที่อ่านออกเป็นคำ เช่น "change-this-to-a-random-secret-key" จึงไม่ถูกฟ้อง
# แต่ค่าอย่าง "8f3a2b9c1d7e4f6a0b5c8d2e9f1a3b7c" ถูกฟ้อง
# ---------------------------------------------------------------------------
PLACEHOLDER_VALUES = re.compile(
    r"""(?ix)^(
        x{3,} | \.{3,} | <[^>]+> | \{\{.*\}\} | \$\{?[A-Z_]+\}? |
        (os\.)?(environ|getenv|environb).* |
        [a-f0-9]{0,7}
    )$""")

# คำที่ถ้าปรากฏในค่า แปลว่าเป็นตัวอย่าง/ให้ไปเปลี่ยนเอง ไม่ใช่ของจริง
PLACEHOLDER_WORDS = re.compile(
    r"(?i)(change|replace|your|placeholder|example|sample|dummy|"
    r"password|passwd|secret|token|apikey|api[-_]key|"
    r"test|fake|foo|bar|baz|hunter2|letmein|admin|"
    r"insert|todo|here|xxx)"
    r"|[฀-๿]")           # มีตัวอักษรไทย = ข้อความอธิบาย ไม่ใช่คีย์


def looks_like_real_secret(value: str) -> bool:
    """ค่านี้หน้าตาเหมือน secret ที่ใช้งานจริงหรือแค่ตัวอย่าง"""
    value = value.strip()
    if len(value) < 8:
        return False
    if PLACEHOLDER_VALUES.match(value):
        return False
    if PLACEHOLDER_WORDS.search(value):
        return False
    if " " in value:                    # ประโยคอธิบาย ไม่ใช่คีย์
        return False
    if re.fullmatch(r"[0-9a-fA-F]{16,}", value):        # hex digest
        return True
    if re.fullmatch(r"[A-Za-z0-9+/=_\-.]{16,}", value):  # base64 / token
        classes = sum([
            bool(re.search(r"[a-z]", value)),
            bool(re.search(r"[A-Z]", value)),
            bool(re.search(r"\d", value)),
            bool(re.search(r"[+/=_\-.]", value)),
        ])
        return classes >= 3
    return False

# ---------------------------------------------------------------------------
# กฎที่ 3 - ข้อมูลส่วนตัว (ทำงานได้โดยไม่ต้องรู้ชื่อจริงของใคร)
# ---------------------------------------------------------------------------
PRIVACY_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("windows-user-path",
     re.compile(r"(?i)[A-Z]:[\\/]+Users[\\/]+(?!Public\b|Default\b)[^\\/\s'\"<>]{2,}"),
     "path ที่มีชื่อ user ของ Windows อยู่ — ใช้ path แบบ relative แทน"),

    ("unix-home-path",
     re.compile(r"(?<![\w.])/(?:home|Users)/(?!runner\b|user\b)[a-z][\w.-]{1,}/"),
     "path ที่มีชื่อ user อยู่"),

    ("onedrive-path",
     re.compile(r"(?i)\bOneDrive[\\/]"),
     "path OneDrive ส่วนตัว"),

    ("email",
     # TLD ต้องเป็นตัวอักษรล้วน ไม่งั้น `brew install python@3.12` จะถูกมองเป็นอีเมล
     re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b"),
     "อีเมล — ใช้ชื่อบทบาท (คนที่ 1/2/3) แทนในเอกสาร"),

    ("student-id",
     # รหัสนักศึกษา/บัตรประชาชนไทย: เลขล้วน 10-13 หลักที่ยืนเดี่ยว
     re.compile(r"(?<![\d.\-v])\b\d{10,13}\b(?![\d.\-])"),
     "เลขยาว 10-13 หลัก อาจเป็นรหัสนักศึกษาหรือเลขบัตรประชาชน"),

    ("thai-phone",
     re.compile(r"(?<!\d)0\d{1,2}[- ]?\d{3}[- ]?\d{4}(?!\d)"),
     "เบอร์โทรศัพท์"),
]

# อีเมล/ค่าที่อนุญาต — ใช้ในเอกสารเป็นตัวอย่างได้
ALLOWED_LITERALS = re.compile(
    r"(?i)@(example\.(com|org|net)|localhost|test|invalid|"
    r"users\.noreply\.github\.com|domain\.com)\b"
    r"|^(noreply|no-reply|admin|user|someone|you)@")


# ---------------------------------------------------------------------------
def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=REPO_ROOT,
                            capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} ล้มเหลว:\n{result.stderr}")
    return result.stdout


def list_files(mode: str) -> list[str]:
    if mode == "all":
        out = git("ls-files")
    else:
        # เฉพาะไฟล์ที่ staged และยังมีอยู่ (ตัด D = deleted ออก)
        out = git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    return [line.strip() for line in out.splitlines() if line.strip()]


def load_local_terms() -> list[str]:
    if not LOCAL_TERMS_FILE.exists():
        return []
    terms = []
    for line in LOCAL_TERMS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            terms.append(line)
    return terms


def read_text(rel: str) -> str | None:
    path = REPO_ROOT / rel
    if not path.is_file():
        return None
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data[:8000]:          # ไฟล์ binary — ข้ามการตรวจเนื้อหา
        return None
    if len(data) > 2_000_000:           # ไฟล์ใหญ่ผิดปกติ — ข้าม แต่เตือนแยก
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


Finding = tuple[str, int, str, str]      # (path, บรรทัด, ชื่อกฎ, รายละเอียด)


def scan_paths(files: list[str]) -> list[Finding]:
    out: list[Finding] = []
    for rel in files:
        for pattern, why in FORBIDDEN_PATHS:
            if re.search(pattern, rel):
                out.append((rel, 0, "forbidden-file", why))
                break
    return out


def scan_contents(files: list[str], local_terms: list[str],
                  check_privacy: bool) -> list[Finding]:
    out: list[Finding] = []
    term_re = None
    if local_terms:
        term_re = re.compile("|".join(re.escape(t) for t in local_terms),
                             re.IGNORECASE)

    for rel in files:
        if rel in CONTENT_SCAN_EXEMPT:
            continue
        text = read_text(rel)
        if text is None:
            continue
        is_doc = rel.endswith((".md", ".txt"))

        for lineno, line in enumerate(text.splitlines(), start=1):
            if "no-secret-check" in line:      # ทางออกให้เคสที่ตั้งใจจริงๆ
                continue

            for name, pattern, why in SECRET_PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                if name == "assigned-secret":
                    if not looks_like_real_secret(match.group(2)):
                        continue
                elif name == "db-url-with-password":
                    if not looks_like_real_secret(match.group("pw")):
                        continue
                out.append((rel, lineno, name, why))

            if check_privacy:
                for name, pattern, why in PRIVACY_PATTERNS:
                    match = pattern.search(line)
                    if not match:
                        continue
                    hit = match.group(0)
                    if ALLOWED_LITERALS.search(hit):
                        continue
                    # เอกสารมักอ้าง path ตัวอย่างในบล็อกโค้ด — ยังเตือนอยู่
                    # แต่ให้ข้อมูลว่าเป็นไฟล์เอกสารเพื่อให้ตัดสินใจง่าย
                    suffix = " (ในไฟล์เอกสาร)" if is_doc else ""
                    out.append((rel, lineno, name, why + suffix))

            if term_re and term_re.search(line):
                out.append((rel, lineno, "personal-term",
                            "ตรงกับคำใน tools/personal_terms.local.txt"))
    return out


# ---------------------------------------------------------------------------
# self-test
#
# ตัวตรวจที่ผ่อนปรนจนไม่ฟ้องอะไรเลย = ไม่มีประโยชน์ และอันตรายกว่าไม่มี
# เพราะทำให้ชะล่าใจ ชุดนี้จึงพิสูจน์สองด้านเสมอ:
#   ต้องจับได้      (ของจริง)
#   ต้องไม่ฟ้อง     (ค่าตัวอย่างในเอกสาร)
# ---------------------------------------------------------------------------
MUST_CATCH = [
    'SECRET_KEY = "8f3a2b9c1d7e4f6a0b5c8d2e9f1a3b7c"',
    'SECRET_KEY = "kQ7xR2mN9pL4vT8wZ3yB6cF1dH5jA0sG"',
    'api_key = "sk-proj-9aZ2xQ7mR4tY8uI3oP6lK1jH5gF0dS"',
    'AWS_ID = "AKIAIOSFODNN7EXAMPLE"',
    "token = ghp_A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8",
    "-----BEGIN RSA PRIVATE KEY-----",
    'DB = "postgresql://luma:Xk7pQ2mR9tZ4wB1n@10.0.0.5:5432/luma"',
]

MUST_NOT_CATCH = [
    'SECRET_KEY = "CHANGE-ME-run-the-secrets-command-above"',
    'SECRET_KEY = "change-this-to-a-random-secret-key"',
    'SECRET_KEY = "ใส่ random key ที่นี่"',
    'SECRET_KEY = os.environ["LUMA_SECRET_KEY"]',
    'password = "password123"',
    'login(client, email="u1@example.com", password="wrongpassword")',
    'SQLALCHEMY_DATABASE_URI = "sqlite:///luma.db"',
    '# "postgresql+psycopg://luma:PASSWORD@192.168.1.40:5432/luma"',
    "เปลี่ยนเป็น `postgresql://user:pass@host:5432/luma`",
    "brew install python@3.12",
    "ดู https://stable-diffusion-art.com/samplers/ ประกอบ",
    "cfg_scale 8-14 ตาม Lecture 2 หน้า 10",
]


def run_self_test() -> int:
    def hits(line: str) -> list[str]:
        found = []
        for name, pattern, _ in SECRET_PATTERNS:
            match = pattern.search(line)
            if not match:
                continue
            if name == "assigned-secret" and not looks_like_real_secret(match.group(2)):
                continue
            if name == "db-url-with-password" and not looks_like_real_secret(
                    match.group("pw")):
                continue
            found.append(name)
        for name, pattern, _ in PRIVACY_PATTERNS:
            match = pattern.search(line)
            if match and not ALLOWED_LITERALS.search(match.group(0)):
                found.append(name)
        return found

    print("=" * 62)
    print("  self-test ของตัวตรวจเอง")
    print("=" * 62)
    failures = 0

    print("\nต้องจับได้:")
    for line in MUST_CATCH:
        names = hits(line)
        ok = bool(names)
        failures += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {line[:52]:<54} {names}")

    print("\nต้องไม่ฟ้อง:")
    for line in MUST_NOT_CATCH:
        names = hits(line)
        ok = not names
        failures += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {line[:52]:<54} {names}")

    total = len(MUST_CATCH) + len(MUST_NOT_CATCH)
    print()
    print("=" * 62)
    if failures:
        print(f"self-test ไม่ผ่าน: {failures}/{total}")
        print("=" * 62)
        return 1
    print(f"self-test ผ่าน {total}/{total}")
    print("=" * 62)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ตรวจว่าไม่มี secret / ฐานข้อมูล / ข้อมูลส่วนตัว หลุดขึ้น git")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--staged", action="store_true",
                       help="ตรวจเฉพาะไฟล์ที่ staged (ค่าเริ่มต้น เหมาะกับ pre-commit)")
    group.add_argument("--all", action="store_true",
                       help="ตรวจไฟล์ที่ track ทั้ง repo")
    parser.add_argument("--no-privacy", action="store_true",
                        help="ข้ามการตรวจข้อมูลส่วนตัว ตรวจแค่ secret")
    parser.add_argument("--self-test", action="store_true",
                        help="ทดสอบตัวตรวจเองว่ายังจับของจริงได้และไม่เตือนผิด")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    mode = "all" if args.all else "staged"
    files = list_files(mode)

    print("=" * 62)
    print(f"  ตรวจ secret / privacy  (โหมด: {mode}, {len(files)} ไฟล์)")
    print("=" * 62)

    if not files:
        print("ไม่มีไฟล์ให้ตรวจ")
        if mode == "staged":
            print("(ยังไม่ได้ git add อะไร — ใช้ --all ถ้าอยากตรวจทั้ง repo)")
        return 0

    local_terms = load_local_terms()
    if local_terms:
        print(f"โหลดคำส่วนตัวจากเครื่อง {len(local_terms)} คำ "
              f"(จาก {LOCAL_TERMS_FILE.name})")
    else:
        print(f"ยังไม่มี {LOCAL_TERMS_FILE.name} — "
              f"ใส่ชื่อเล่น/อีเมลของตัวเองไว้ในนั้นได้ ไฟล์ไม่ขึ้น git")
    print()

    findings = scan_paths(files) + scan_contents(files, local_terms,
                                                 check_privacy=not args.no_privacy)

    if not findings:
        print("=" * 62)
        print(f"ผ่าน: ตรวจ {len(files)} ไฟล์ ไม่พบ secret หรือข้อมูลส่วนตัว")
        print("=" * 62)
        return 0

    by_file: dict[str, list[Finding]] = {}
    for finding in findings:
        by_file.setdefault(finding[0], []).append(finding)

    for rel in sorted(by_file):
        print(f"[FAIL] {rel}")
        for _, lineno, name, why in by_file[rel]:
            where = f"บรรทัด {lineno}" if lineno else "ทั้งไฟล์"
            print(f"          {where}  [{name}] {why}")
        print()

    print("=" * 62)
    print(f"ไม่ผ่าน: พบ {len(findings)} จุด ใน {len(by_file)} ไฟล์")
    print()
    print("วิธีแก้")
    print("  ไฟล์ที่ไม่ควรขึ้น git :  git rm --cached <ไฟล์>  แล้วเช็คว่า .gitignore ครอบ")
    print("  secret ในโค้ด        :  ย้ายไป instance/config.py (ไฟล์นี้ถูก ignore อยู่)")
    print("  ข้อมูลส่วนตัว        :  ใช้ชื่อบทบาท (คนที่ 1/2/3) และ path แบบ relative")
    print("  เตือนผิด (false alarm):  เติมคำว่า  no-secret-check  ท้ายบรรทัดนั้น")
    print()
    print("ถ้า commit ไปแล้วและ push ขึ้น GitHub แล้ว")
    print("  ถือว่าค่านั้น 'หลุด' ไปแล้ว ต้อง revoke/เปลี่ยนค่าใหม่")
    print("  การลบ commit ทีหลังไม่ช่วย เพราะอาจถูก cache/clone ไปแล้ว")
    print("=" * 62)
    return 1


if __name__ == "__main__":
    sys.exit(main())
