/**
 * LUMA — หน้าจัดการผู้ใช้ (admin.html)
 * -------------------------------------------------------------------------
 * 1. โหลดรายชื่อจาก GET /api/admin/users แล้ววาดเป็นตาราง 1 แถวต่อ 1 คน
 * 2. กด "บันทึก" ของแถวไหน ส่งเฉพาะช่องที่แก้ของแถวนั้นไป PATCH /api/admin/users/<id>
 *
 * สิทธิ์เช็คที่ server — หน้านี้แค่แสดงข้อความตามที่ server ตอบ (401 / 403)
 *
 * ห้าม hardcode localhost/IP — อ่าน API base จาก window.LUMA_CONFIG เท่านั้น
 */

(() => {
  const API_BASE = window.LUMA_CONFIG ? window.LUMA_CONFIG.apiBase : "";

  const errorBox = document.getElementById("admin-error");
  const table = document.getElementById("admin-table");
  const rows = document.getElementById("admin-rows");

  function showError(message) {
    errorBox.textContent = message;
    errorBox.removeAttribute("hidden");
  }

  async function loadUsers() {
    let res;
    try {
      res = await fetch(`${API_BASE}/api/admin/users`, { credentials: "include" });
    } catch (err) {
      showError("เชื่อมต่อเซิร์ฟเวอร์ไม่ได้");
      return;
    }

    if (res.status === 401) {
      // ยังไม่ได้ล็อกอิน -> ส่งไปหน้าเข้าสู่ระบบ
      window.location.href = "login.html";
      return;
    }
    if (res.status === 403) {
      showError("หน้านี้ใช้ได้เฉพาะผู้ดูแลระบบ");
      return;
    }
    if (!res.ok) {
      showError(`โหลดรายชื่อไม่สำเร็จ (HTTP ${res.status})`);
      return;
    }

    const data = await res.json();
    for (const user of data.items) {
      rows.appendChild(buildRow(user));
    }
    table.removeAttribute("hidden");
  }

  // สร้างช่องกรอก 1 ช่อง พร้อมค่าเริ่มต้น
  function makeInput(type, value) {
    const input = document.createElement("input");
    input.type = type;
    input.value = value;
    return input;
  }

  // สร้าง <td> ที่มีของ 1 ชิ้นอยู่ข้างใน
  function makeCell(child) {
    const cell = document.createElement("td");
    cell.appendChild(child);
    return cell;
  }

  // สร้างแถวของผู้ใช้ 1 คน
  // ใส่ค่าด้วย .value / .textContent เท่านั้น ไม่ต่อสตริงเป็น HTML
  // เพราะชื่อเป็นข้อความที่ผู้ใช้ตั้งเอง ถ้าต่อเป็น HTML คนที่ตั้งชื่อเป็น <script>
  // จะรันโค้ดในหน้าของ admin ได้
  function buildRow(user) {
    const nameInput = makeInput("text", user.displayName);
    const emailInput = makeInput("email", user.email);
    const passwordInput = makeInput("password", "");
    passwordInput.placeholder = "เว้นว่าง = ไม่เปลี่ยน";
    passwordInput.autocomplete = "new-password";

    const saveButton = document.createElement("button");
    saveButton.type = "button";
    saveButton.textContent = "บันทึก";

    const status = document.createElement("span");
    status.className = "admin-status";

    const lastCell = makeCell(saveButton);
    lastCell.appendChild(status);

    const row = document.createElement("tr");
    row.appendChild(makeCell(document.createTextNode(user.id)));
    row.appendChild(makeCell(nameInput));
    row.appendChild(makeCell(emailInput));
    row.appendChild(makeCell(document.createTextNode(user.role)));
    row.appendChild(makeCell(passwordInput));
    row.appendChild(lastCell);

    saveButton.addEventListener("click", () => {
      saveRow(user, nameInput, emailInput, passwordInput, saveButton, status);
    });

    return row;
  }

  function setStatus(status, kind, message) {
    status.className = `admin-status admin-status--${kind}`;
    status.textContent = message;
  }

  async function saveRow(user, nameInput, emailInput, passwordInput, saveButton, status) {
    // เก็บเฉพาะช่องที่ต่างจากค่าเดิม — ช่องที่ไม่ได้แก้จะไม่ถูกส่งไป
    const changes = {};
    if (nameInput.value.trim() !== user.displayName) {
      changes.displayName = nameInput.value.trim();
    }
    if (emailInput.value.trim() !== user.email) {
      changes.email = emailInput.value.trim();
    }
    if (passwordInput.value !== "") {
      changes.password = passwordInput.value;
    }

    if (Object.keys(changes).length === 0) {
      setStatus(status, "error", "ยังไม่ได้แก้อะไร");
      return;
    }

    saveButton.disabled = true;
    try {
      const res = await fetch(`${API_BASE}/api/admin/users/${user.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          ...window.csrfHeaders(),
        },
        credentials: "include",
        body: JSON.stringify(changes),
      });
      const data = await res.json();

      if (!res.ok) {
        setStatus(status, "error", data.error || `บันทึกไม่สำเร็จ (HTTP ${res.status})`);
        return;
      }

      // จำค่าที่ server บันทึกจริงไว้เป็น "ค่าเดิม" ของรอบถัดไป
      // แล้วเขียนกลับลงช่อง เพราะ server อาจปรับค่า (เช่น อีเมลเป็นตัวพิมพ์เล็ก)
      user.displayName = data.user.displayName;
      user.email = data.user.email;
      nameInput.value = user.displayName;
      emailInput.value = user.email;
      passwordInput.value = "";
      setStatus(status, "ok", "บันทึกแล้ว");
    } catch (err) {
      setStatus(status, "error", "เชื่อมต่อเซิร์ฟเวอร์ไม่ได้");
    } finally {
      saveButton.disabled = false;
    }
  }

  loadUsers();
})();
