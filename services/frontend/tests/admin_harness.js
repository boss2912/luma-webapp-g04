// รัน admin.js และ layout.js ตัวจริงบน DOM จำลอง ทดสอบหน้าจัดการผู้ใช้ (#228)
// เรียกจาก test_admin_page.py:
//   node admin_harness.js <scenario> <path/to/admin.js> <path/to/layout.js>
const fs = require("fs");
const vm = require("vm");
const [scenario, adminPath, layoutPath] = process.argv.slice(2);

// element จำลอง 1 ตัว — จำลูกที่ถูก appendChild และ attribute ที่ถูกลบไว้ให้ test ถามได้
function el(tag = "div", extra = {}) {
  const handlers = {};
  const node = {
    tag, textContent: "", innerHTML: "", className: "", value: "", type: "",
    style: {}, dataset: {}, children: [], removed: [], disabled: false,
    addEventListener(type, fn) { handlers[type] = fn; },
    fire(type, e = {}) { return handlers[type] ? handlers[type](e) : undefined; },
    has(type) { return Boolean(handlers[type]); },
    setAttribute() {},
    removeAttribute(name) { node.removed.push(name); },
    appendChild(child) { node.children.push(child); return child; },
    querySelectorAll: () => [],
    ...extra,
  };
  return node;
}

const sleep = () => new Promise((r) => setTimeout(r, 0));
const settle = async () => { for (let i = 0; i < 5; i += 1) await sleep(); };

function jsonResponse(status, body) {
  return { ok: status >= 200 && status < 300, status, json: async () => body, text: async () => "" };
}

const TWO_USERS = { items: [
  { id: 1, displayName: "admin", email: "admin@example.com", role: "admin" }, // no-secret-check
  { id: 2, displayName: "Boss", email: "boss@example.com", role: "user" }, // no-secret-check
] };

// ------------------------------------------------------------------ admin.js

function loadAdmin({ listImpl, patchImpl }) {
  const errorBox = el("p");
  const table = el("table");
  const rows = el("tbody");
  const nodes = { "admin-error": errorBox, "admin-table": table, "admin-rows": rows };
  const location = { href: "" };
  const requests = [];

  const ctx = {
    window: { csrfHeaders: () => ({ "X-CSRFToken": "t" }), location },
    console: { error() {}, log() {} },
    document: {
      getElementById: (id) => nodes[id] || null,
      createElement: (tag) => el(tag),
      createTextNode: (text) => ({ tag: "#text", textContent: String(text) }),
    },
    fetch: async (url, opts = {}) => {
      requests.push({ url, method: opts.method || "GET", headers: opts.headers || {}, body: opts.body });
      if (url.endsWith("/api/admin/users")) return listImpl();
      if (url.includes("/api/admin/users/")) return patchImpl(url, opts);
      throw new Error("unexpected fetch " + url);
    },
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(adminPath, "utf8"), ctx);
  return { errorBox, table, rows, location, requests };
}

// แถวที่ admin.js สร้าง: td ลำดับ 0 id · 1 ชื่อ · 2 อีเมล · 3 สิทธิ์ · 4 รหัสใหม่ · 5 ปุ่ม + สถานะ
function parts(row) {
  const cells = row.children;
  return {
    name: cells[1].children[0],
    email: cells[2].children[0],
    password: cells[4].children[0],
    button: cells[5].children[0],
    status: cells[5].children[1],
  };
}

async function adminScenario() {
  if (scenario === "load_lists_users") {
    const env = loadAdmin({ listImpl: async () => jsonResponse(200, TWO_USERS) });
    await settle();
    const second = parts(env.rows.children[1]);
    return {
      rowCount: env.rows.children.length,
      tableShown: env.table.removed.includes("hidden"),
      secondName: second.name.value,
      secondEmail: second.email.value,
      secondPassword: second.password.value,
    };
  }

  if (scenario === "load_401_redirects_to_login") {
    const env = loadAdmin({ listImpl: async () => jsonResponse(401, { error: "Unauthorized" }) });
    await settle();
    return { redirectedTo: env.location.href, rowCount: env.rows.children.length };
  }

  if (scenario === "load_403_shows_error") {
    const env = loadAdmin({ listImpl: async () => jsonResponse(403, { error: "Admin only" }) });
    await settle();
    return {
      redirectedTo: env.location.href,
      errorShown: env.errorBox.removed.includes("hidden"),
      errorText: env.errorBox.textContent,
      tableShown: env.table.removed.includes("hidden"),
    };
  }

  if (scenario === "save_sends_only_changed_fields") {
    const env = loadAdmin({
      listImpl: async () => jsonResponse(200, TWO_USERS),
      patchImpl: async () => jsonResponse(200, {
        status: "success",
        user: { id: 2, displayName: "Boss2", email: "boss@example.com", role: "user" }, // no-secret-check
      }),
    });
    await settle();
    const row = parts(env.rows.children[1]);
    row.name.value = "Boss2";            // แก้ชื่ออย่างเดียว อีเมลกับรหัสไม่แตะ
    await row.button.fire("click");
    await settle();
    const patch = env.requests.find((r) => r.method === "PATCH");
    return {
      url: patch.url,
      body: JSON.parse(patch.body),
      csrf: patch.headers["X-CSRFToken"],
      statusText: row.status.textContent,
      statusClass: row.status.className,
      buttonDisabled: row.button.disabled,
    };
  }

  if (scenario === "save_password_only") {
    const env = loadAdmin({
      listImpl: async () => jsonResponse(200, TWO_USERS),
      patchImpl: async () => jsonResponse(200, { status: "success", user: TWO_USERS.items[1] }),
    });
    await settle();
    const row = parts(env.rows.children[1]);
    row.password.value = "new-password"; // no-secret-check
    await row.button.fire("click");
    await settle();
    const patch = env.requests.find((r) => r.method === "PATCH");
    return { body: JSON.parse(patch.body), passwordBoxAfter: row.password.value };
  }

  if (scenario === "save_nothing_changed_sends_no_request") {
    const env = loadAdmin({ listImpl: async () => jsonResponse(200, TWO_USERS) });
    await settle();
    const row = parts(env.rows.children[1]);
    await row.button.fire("click");
    await settle();
    return {
      patchCount: env.requests.filter((r) => r.method === "PATCH").length,
      statusText: row.status.textContent,
      statusClass: row.status.className,
    };
  }

  if (scenario === "save_error_shows_server_message") {
    const env = loadAdmin({
      listImpl: async () => jsonResponse(200, TWO_USERS),
      patchImpl: async () => jsonResponse(400, { error: "taken" }),
    });
    await settle();
    const row = parts(env.rows.children[1]);
    row.email.value = "admin@example.com"; // no-secret-check
    await row.button.fire("click");
    await settle();
    return {
      statusText: row.status.textContent,
      statusClass: row.status.className,
      emailBoxAfter: row.email.value,
      buttonDisabled: row.button.disabled,
    };
  }

  return null;
}

// ----------------------------------------------------------------- layout.js

async function layoutScenario() {
  const roles = { layout_admin_gets_admin_link: "admin", layout_user_gets_no_admin_link: "user" };
  if (!(scenario in roles)) return null;

  const inserted = [];
  const navSlot = el();
  const userSlot = el("div", {
    parentNode: { insertBefore(node, before) { inserted.push({ node, beforeUserSlot: before === userSlot }); } },
  });
  const nodes = { "app-nav-slot": navSlot, "nav-user-slot": userSlot };

  const ctx = {
    window: { csrfHeaders: () => ({}), location: { href: "" } },
    console: { error() {}, log() {} },
    alert() {},
    localStorage: { removeItem() {}, setItem() {}, getItem() {} },
    document: {
      readyState: "complete",
      body: { dataset: { page: "generate" } },
      getElementById: (id) => nodes[id] || null,
      querySelectorAll: () => [],
      querySelector: () => null,
      createElement: (tag) => el(tag),
      addEventListener() {},
    },
    fetch: async (url) => {
      if (url.endsWith("/partials/nav.html")) return { ok: true, status: 200, text: async () => "" };
      if (url.endsWith("/api/auth/me")) {
        return jsonResponse(200, { email: "demo@luma.local", displayName: "demo", role: roles[scenario] }); // no-secret-check
      }
      throw new Error("unexpected fetch " + url);
    },
  };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(layoutPath, "utf8"), ctx);
  await settle();

  const links = inserted.filter((item) => item.node.tag === "a");
  return {
    linkCount: links.length,
    href: links.length ? links[0].node.href : "",
    text: links.length ? links[0].node.textContent : "",
    beforeUserSlot: links.length ? links[0].beforeUserSlot : false,
  };
}

async function main() {
  const result = (await adminScenario()) || (await layoutScenario());
  if (result === null) throw new Error(`ไม่รู้จัก scenario: ${scenario}`);
  console.log(JSON.stringify(result));
}

main();
