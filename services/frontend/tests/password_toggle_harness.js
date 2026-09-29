// รัน password-toggle.js ตัวจริงบน DOM จำลอง แล้วพิมพ์ผลเป็น JSON บรรทัดสุดท้าย
// เรียกจาก test_password_toggle.py:  node password_toggle_harness.js <scenario> <path/to/password-toggle.js>
const fs = require("fs");
const vm = require("vm");
const [scenario, scriptPath] = process.argv.slice(2);

function el(extra = {}) {
  const handlers = {};
  return {
    hidden: false, type: "password",
    setAttribute(k, v) { this[k] = v; },
    getAttribute(k) { return this[k]; },
    addEventListener(type, fn) { handlers[type] = fn; },
    fire(type, e = {}) { return handlers[type] ? handlers[type](e) : undefined; },
    ...extra,
  };
}

function buildField() {
  const input = el({ type: "password" });
  const eye = el({ hidden: false });
  const eyeOff = el({ hidden: true });
  const btn = el({
    querySelector(sel) { return sel === ".auth-field__eye" ? eye : sel === ".auth-field__eye-off" ? eyeOff : null; },
    closest() { return wrap; },
  });
  const wrap = { querySelector: () => input };
  return { input, eye, eyeOff, btn };
}

function load(fields) {
  const ctx = {
    document: {
      readyState: "complete",
      addEventListener() {},
      querySelectorAll: (sel) => (sel === ".auth-field__toggle" ? fields.map((f) => f.btn) : []),
    },
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(scriptPath, "utf8"), ctx);
}

function main() {
  if (scenario === "single_click_shows_password") {
    const field = buildField();
    load([field]);
    field.btn.fire("click");
    console.log(JSON.stringify({
      inputType: field.input.type,
      eyeHidden: field.eye.hidden,
      eyeOffHidden: field.eyeOff.hidden,
      ariaLabel: field.btn.getAttribute("aria-label"),
      ariaPressed: field.btn.getAttribute("aria-pressed"),
    }));
    return;
  }

  if (scenario === "second_click_hides_password_again") {
    const field = buildField();
    load([field]);
    field.btn.fire("click");
    field.btn.fire("click");
    console.log(JSON.stringify({
      inputType: field.input.type,
      eyeHidden: field.eye.hidden,
      eyeOffHidden: field.eyeOff.hidden,
      ariaLabel: field.btn.getAttribute("aria-label"),
    }));
    return;
  }

  if (scenario === "two_fields_are_independent") {
    const a = buildField();
    const b = buildField();
    load([a, b]);
    a.btn.fire("click"); // แสดงเฉพาะช่องแรก
    console.log(JSON.stringify({
      aType: a.input.type,
      bType: b.input.type,
    }));
    return;
  }

  throw new Error(`ไม่รู้จัก scenario: ${scenario}`);
}

main();
