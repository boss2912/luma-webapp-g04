// รัน pnginfo.js ตัวจริงบน DOM จำลอง + fetch ที่ควบคุมได้ แล้วพิมพ์ผลเป็น JSON บรรทัดสุดท้าย
// เรียกจาก test_pnginfo_page.py:  node pnginfo_harness.js <scenario> <path/to/pnginfo.js>
const fs = require("fs");
const vm = require("vm");
const [scenario, scriptPath] = process.argv.slice(2);

function el(extra = {}) {
  const handlers = {};
  return {
    textContent: "", value: "", disabled: false, hidden: false, files: null, src: "",
    classList: { add() {}, remove() {} },
    setAttribute(k, v) { this[k === "class" ? "className" : k] = v; if (k === "hidden") this.hidden = true; },
    removeAttribute(k) { if (k === "hidden") this.hidden = false; },
    addEventListener(type, fn) { handlers[type] = fn; },
    fire(type, event = {}) { return handlers[type] ? handlers[type](event) : undefined; },
    has(type) { return Boolean(handlers[type]); },
    ...extra,
  };
}

function load({ fetchImpl } = {}) {
  const nodes = {};
  ["pi-upload", "pi-submit", "pi-error", "pi-preview-container", "pi-preview-img",
    "pi-placeholder", "pi-result", "pi-result-title", "pi-parameters"].forEach((id) => {
    nodes[id] = el();
  });
  nodes["pi-error"].hidden = true;
  nodes["pi-result"].hidden = true;
  nodes["pi-preview-img"].hidden = true;
  nodes["pi-submit"].disabled = true;

  class FakeFileReader {
    readAsDataURL() { this.result = "data:image/png;base64,UE5H"; this.onload(); }
  }

  const ctx = {
    window: { csrfHeaders: () => ({ "X-CSRFToken": "t" }) },
    console: { error() {}, log() {} },
    fetch: fetchImpl,
    FileReader: FakeFileReader,
    document: {
      readyState: "complete",
      getElementById: (id) => nodes[id] || null,
      addEventListener() {},
    },
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(scriptPath, "utf8"), ctx);
  return { nodes };
}

function pickFile(env, { type = "image/png", name = "a.png" } = {}) {
  env.nodes["pi-upload"].files = [{ type, name }];
  env.nodes["pi-upload"].fire("change");
}

const sleep = () => new Promise((r) => setTimeout(r, 0));

async function main() {
  if (scenario === "start") {
    const env = load();
    console.log(JSON.stringify({
      submitDisabled: env.nodes["pi-submit"].disabled,
      resultHidden: env.nodes["pi-result"].hidden,
    }));
    return;
  }

  if (scenario === "select_non_png") {
    const env = load();
    pickFile(env, { type: "image/jpeg", name: "a.jpg" });
    console.log(JSON.stringify({
      error: env.nodes["pi-error"].textContent,
      errorHidden: env.nodes["pi-error"].hidden,
      submitDisabled: env.nodes["pi-submit"].disabled,
      previewHidden: env.nodes["pi-preview-img"].hidden,
    }));
    return;
  }

  if (scenario === "select_png") {
    const env = load();
    pickFile(env);
    console.log(JSON.stringify({
      submitDisabled: env.nodes["pi-submit"].disabled,
      previewHidden: env.nodes["pi-preview-img"].hidden,
      previewSrc: env.nodes["pi-preview-img"].src,
      errorHidden: env.nodes["pi-error"].hidden,
    }));
    return;
  }

  if (scenario === "read_found") {
    let sent = null;
    const env = load({
      fetchImpl: async (url, opts) => {
        sent = { url, body: JSON.parse(opts.body), headers: opts.headers };
        return { ok: true, status: 200, json: async () => ({ parameters: "a fox\nSteps: 20", found: true }) };
      },
    });
    pickFile(env);
    await env.nodes["pi-submit"].fire("click");
    await sleep();
    console.log(JSON.stringify({
      url: sent.url, sentImage: sent.body.image, hasCsrf: Boolean(sent.headers["X-CSRFToken"]),
      resultHidden: env.nodes["pi-result"].hidden,
      title: env.nodes["pi-result-title"].textContent,
      parameters: env.nodes["pi-parameters"].textContent,
      submitDisabled: env.nodes["pi-submit"].disabled,
    }));
    return;
  }

  if (scenario === "read_not_found") {
    const env = load({
      fetchImpl: async () => ({ ok: true, status: 200, json: async () => ({ parameters: null, found: false }) }),
    });
    pickFile(env);
    await env.nodes["pi-submit"].fire("click");
    await sleep();
    console.log(JSON.stringify({
      resultHidden: env.nodes["pi-result"].hidden,
      title: env.nodes["pi-result-title"].textContent,
      parameters: env.nodes["pi-parameters"].textContent,
    }));
    return;
  }

  if (scenario === "read_error") {
    const env = load({
      fetchImpl: async () => ({ ok: false, status: 400, json: async () => ({ error: "image must be a PNG file" }) }),
    });
    pickFile(env);
    await env.nodes["pi-submit"].fire("click");
    await sleep();
    console.log(JSON.stringify({
      error: env.nodes["pi-error"].textContent,
      errorHidden: env.nodes["pi-error"].hidden,
      resultHidden: env.nodes["pi-result"].hidden,
      submitDisabled: env.nodes["pi-submit"].disabled,
    }));
    return;
  }

  throw new Error(`ไม่รู้จัก scenario: ${scenario}`);
}

main();
