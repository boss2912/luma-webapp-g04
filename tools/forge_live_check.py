"""
ทดสอบ LUMA กับ Forge ตัวจริง — ยิงน้อย steps ต่ำ (รวมสร้างภาพไม่เกิน 9 ครั้ง ครั้งละ 6 steps)

ใช้:  python forge_live_check.py --forge https://xxxx.gradio.live --repo /path/to/luma-webapp-g04
      (--skip-stack = ทดสอบแค่ Forge ตรงๆ ไม่ต้องเปิด ai-engine/backend)

ส่วน A — Forge ตรงๆ:   API เปิดไหม · sampler ที่ LUMA รับมีใน Forge ครบไหม · seed เดิมได้ภาพเดิมไหม
                        · prompt แปลกๆ ที่ fuzz เจอ ทำ Forge จริงพังจริงไหม
ส่วน B — ทั้งระบบ:     ai-engine + backend (+worker) ของ repo ชี้ไป Forge จริง แล้วสมัคร/ล็อกอิน/สร้างภาพ
                        ผ่าน /api/* แบบหน้าเว็บ · ภาพที่ได้เป็นภาพจริง · 3 ฟังก์ชันหน้า Function บนภาพจริง
"""
import argparse, base64, hashlib, io, os, socket, subprocess, sys, tempfile, time
import requests
from PIL import Image, ImageStat

ap = argparse.ArgumentParser()
ap.add_argument("--forge", required=True)
ap.add_argument("--repo", default=".")
ap.add_argument("--python", default=sys.executable)
ap.add_argument("--skip-stack", action="store_true")
args = ap.parse_args()
F = args.forge.rstrip("/")
rows = []


def rec(part, name, ok, detail=""):
    rows.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} [{part}] {name}" + (f"  — {detail}" if detail else ""), flush=True)


def txt2img(prompt, seed=1234, steps=6, sampler="Euler a"):
    r = requests.post(F + "/sdapi/v1/txt2img", timeout=300, json={
        "prompt": prompt, "steps": steps, "seed": seed, "width": 512, "height": 512,
        "cfg_scale": 8, "sampler_name": sampler})
    return r


# ---------------------------------------------------------------- A. Forge ตรงๆ
r = requests.get(F + "/sdapi/v1/sd-models", timeout=60)
rec("A", "API เปิด (--api)", r.status_code == 200, f"HTTP {r.status_code} · โมเดล {len(r.json()) if r.ok else '-'} ตัว")
r = requests.get(F + "/sdapi/v1/samplers", timeout=60)
forge_samplers = {s["name"] for s in r.json()} if r.ok else set()
luma_plain = {"Euler a", "Euler", "DDIM", "DPM++ 2M", "DPM++ SDE", "DPM++ 2M SDE"}   # ชื่อที่ ai-engine ส่งถึง Forge จริง
missing = sorted(luma_plain - forge_samplers)
rec("A", "sampler ที่ LUMA ส่งไปมีใน Forge ครบ", not missing, f"ขาด {missing}" if missing else f"Forge มี {len(forge_samplers)} ตัว")

t = time.time(); a = txt2img("a red apple on a wooden table"); dt = time.time() - t
b = txt2img("a red apple on a wooden table")
same = a.ok and b.ok and a.json()["images"][0] == b.json()["images"][0]
rec("A", "seed เดิม = ภาพเดิม (ทำซ้ำได้)", same, f"6 steps ใช้ {dt:.1f}s")
img = Image.open(io.BytesIO(base64.b64decode(a.json()["images"][0]))) if a.ok else None
if img:
    spread = max(ImageStat.Stat(img.convert("L")).stddev[0], 0)
    rec("A", "เป็นภาพที่สร้างจริง ไม่ใช่ภาพสีเดียว", spread > 10, f"{img.size} · ค่าเบี่ยงเบนความสว่าง {spread:.1f}")

for prompt, expect_ok in [("(cat", True), ("(cat:str0.8)", True), ("(cat:1.2.3)", False), ("[cat:dog:1e309]", False)]:
    r = txt2img(prompt, steps=4)
    rec("A", f"Forge กับ {prompt!r} {'ต้องผ่าน' if expect_ok else 'คาดว่าพัง (LUMA กันไว้แล้ว #221)'}",
        r.ok == expect_ok, f"HTTP {r.status_code} {r.text[:80] if not r.ok else ''}")

if args.skip_stack:
    print(f"\n{sum(rows)}/{len(rows)} ผ่าน"); sys.exit(0 if all(rows) else 1)

# ---------------------------------------------------------------- B. ทั้งระบบ
def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

repo = os.path.abspath(args.repo); work = tempfile.mkdtemp(prefix="luma-live-")
ai_port, be_port = free_port(), free_port()
env = dict(os.environ, FORGE_URL=F, AI_ENGINE_PORT=str(ai_port), LUMA_DATABASE_URI=f"sqlite:///{work}/luma.db")
subprocess.run([args.python, "-c", "from migrate_app import create_migration_app; from flask_migrate import upgrade\n"
                "with create_migration_app().app_context(): upgrade()"], cwd=f"{repo}/services/database", env=env, check=True,
               capture_output=True)
runner = (f"import sys; sys.path.insert(0, {repo + '/services/backend'!r})\n"
          "from app import create_app\nfrom app.services.job_queue import start_worker\n"
          f"app = create_app({{'SQLALCHEMY_DATABASE_URI': 'sqlite:///{work}/luma.db', 'SECRET_KEY': 'live-check',"
          f" 'AI_ENGINE_URL': 'http://127.0.0.1:{ai_port}', 'FORGE_TIMEOUT_SECONDS': 300}})\n"
          f"app.instance_path = {work!r}\nstart_worker(app)\napp.run(host='127.0.0.1', port={be_port})\n")
procs = [subprocess.Popen([args.python, "app.py"], cwd=f"{repo}/services/ai-engine", env=env,
                          stdout=open(f"{work}/ai.log", "w"), stderr=subprocess.STDOUT),
         subprocess.Popen([args.python, "-c", runner], stdout=open(f"{work}/backend.log", "w"), stderr=subprocess.STDOUT)]
B = f"http://127.0.0.1:{be_port}"
try:
    for _ in range(60):
        try:
            if requests.get(B + "/health", timeout=1).ok and requests.get(f"http://127.0.0.1:{ai_port}/health", timeout=1).ok: break
        except requests.ConnectionError: pass
        time.sleep(1)
    s = requests.Session(); s.get(B + "/pages/login.html"); s.headers["X-CSRFToken"] = s.cookies.get("csrf_token", "")
    s.post(B + "/api/auth/register", json={"email": "live@luma.test", "displayName": "live", "password": "password123"})
    rec("B", "login", s.post(B + "/api/auth/login", json={"email": "live@luma.test", "password": "password123"}).ok)
    ck = s.get(B + "/api/checkpoints")
    rec("B", "รายชื่อ checkpoint ผ่าน backend -> ai-engine -> Forge", ck.ok, f"{len(ck.json().get('items', []))} ตัว" if ck.ok else ck.text[:80])

    for prompt, sampler in [("a cozy cabin in snowy mountains, (warm light:1.2)", "DPM++ 2M Karras"), ("portrait of an astronaut", "Euler a")]:
        job = s.post(B + "/api/generate", json={"prompt": prompt, "steps": 6, "seed": 42, "sampler_name": sampler})
        if not job.ok:
            rec("B", f"generate {sampler}", False, job.text[:80]); continue
        jid, t = job.json()["job_id"], time.time()
        while time.time() - t < 360:
            st = s.get(f"{B}/api/jobs/{jid}").json()
            if st["status"] in ("done", "failed"): break
            time.sleep(1)
        rec("B", f"generate ครบสาย ({sampler})", st["status"] == "done", f"{time.time() - t:.1f}s · seed_used {st.get('seed_used')} · {st.get('error') or ''}")
    assets = s.get(B + "/api/assets").json()["items"]
    if assets:
        raw = s.get(f"{B}/api/assets/{assets[0]['id']}/image").content
        rec("B", "โหลดภาพจริงกลับมาได้", raw[:4] == b"\x89PNG", f"{len(raw)} bytes · tags {assets[0]['tags']}")
        b64 = base64.b64encode(raw).decode()
        for route, body in [("blur-region", {"region": {"x": 100, "y": 100, "width": 200, "height": 200}, "size": 15}),
                            ("find-objects", {}), ("remove-background", {"region": {"x": 100, "y": 100, "width": 200, "height": 200}}),
                            ("palette/extract", {})]:
            r = s.post(f"{B}/api/pipeline/{route}", json=dict(body, image=b64))
            rec("B", f"หน้า Function: {route} บนภาพจริง", r.ok, f"HTTP {r.status_code}")
    bad = s.post(B + "/api/generate", json={"prompt": "(cat:1.2.3)"})
    rec("B", "LUMA กัน (cat:1.2.3) ก่อนถึง Forge", bad.status_code == 400, f"HTTP {bad.status_code} (ต้องมี #221 ถึงจะผ่าน)")
finally:
    for p in procs: p.terminate()
print(f"\n{sum(rows)}/{len(rows)} ผ่าน · log อยู่ที่ {work}")
