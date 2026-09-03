/**
 * LUMA — Register Logic (Real Backend API)
 * -------------------------------------------------------------------------
 * เชื่อมฟอร์มสมัครสมาชิกเข้ากับ POST /api/auth/register ของจริง
 * อ้างอิง: Issue #49, #50, docs/API_CONTRACT.md
 */

const API_BASE = window.LUMA_CONFIG ? window.LUMA_CONFIG.apiBase : "http://127.0.0.1:5000";
const MIN_PASSWORD_LENGTH = 8;

function initRegisterForm() {
  const form = document.getElementById("register-form");
  if (!form) return;

  const errorBox = document.getElementById("register-error");
  const submitBtn = document.getElementById("register-submit");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideError();

    const displayName = form.displayName.value.trim();
    const email = form.email.value.trim();
    const password = form.password.value;
    const confirmPassword = form.confirmPassword.value;

    const validationError = validate({
      displayName,
      email,
      password,
      confirmPassword,
    });
    if (validationError) {
      showError(validationError);
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ displayName, email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "สมัครสมาชิกไม่สำเร็จ กรุณาตรวจสอบข้อมูลอีกครั้ง");
      }

      // สมัครสำเร็จ ให้พาไปหน้า login พร้อมข้อความแจ้ง
      alert("สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ");
      window.location.href = "login.html";
    } catch (err) {
      showError(err.message || "เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    } finally {
      setLoading(false);
    }
  });

  function validate({ displayName, email, password, confirmPassword }) {
    if (!displayName || !email || !password || !confirmPassword) {
      return "กรุณากรอกข้อมูลให้ครบทุกช่อง";
    }
    if (password.length < MIN_PASSWORD_LENGTH) {
      return `รหัสผ่านต้องยาวอย่างน้อย ${MIN_PASSWORD_LENGTH} ตัวอักษร`;
    }
    if (password !== confirmPassword) {
      return "รหัสผ่านทั้งสองช่องไม่ตรงกัน";
    }
    return null;
  }

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
    submitBtn.textContent = isLoading ? "กำลังบันทึกข้อมูล…" : "สมัครสมาชิก";
  }
}

document.addEventListener("DOMContentLoaded", initRegisterForm);
