/**
 * LUMA — Login Logic (Real Backend API)
 * -------------------------------------------------------------------------
 * เชื่อมฟอร์มเข้าสู่ระบบเข้ากับ POST /api/auth/login ของจริง
 * อ้างอิง: Issue #50, docs/API_CONTRACT.md
 */

const API_BASE = window.LUMA_CONFIG ? window.LUMA_CONFIG.apiBase : "http://127.0.0.1:5000";

function initLoginForm() {
  const form = document.getElementById("login-form");
  if (!form) return;

  const errorBox = document.getElementById("login-error");
  const submitBtn = document.getElementById("login-submit");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideError();

    const email = form.email.value.trim();
    const password = form.password.value;

    if (!email || !password) {
      showError("กรุณากรอกอีเมลและรหัสผ่านให้ครบถ้วน");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // ส่ง session cookie ข้าม domain
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        if (res.status === 429) {
          throw new Error("พยายามเข้าสู่ระบบบ่อยเกินไป กรุณารอสักครู่");
        }
        throw new Error(data.error || "อีเมลหรือรหัสผ่านไม่ถูกต้อง");
      }

      // บันทึก email ใน localStorage เพื่อให้ frontend แสดงชื่อใน header ได้ทันที
      localStorage.setItem("luma_user_email", email);

      // เข้าสู่ระบบสำเร็จ พาไปหน้าสร้างภาพ
      window.location.href = "generate.html";
    } catch (err) {
      showError(err.message || "เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    } finally {
      setLoading(false);
    }
  });

  function showError(message) {
    errorBox.textContent = message;
    errorBox.removeAttribute("hidden");
  }

  function hideError() {
    errorBox.textContent = "";
    errorBox.setAttribute("hidden", "");
  }

  function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    submitBtn.textContent = isLoading ? "กำลังตรวจสอบข้อมูล…" : "เข้าสู่ระบบ";
  }
}

document.addEventListener("DOMContentLoaded", initLoginForm);
