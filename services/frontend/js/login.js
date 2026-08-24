/**
 * LUMA — Login form
 * -------------------------------------------------------------------------
 * ตอนนี้ยังไม่มี endpoint จริงให้เรียก เพราะ:
 *   - #32 [TEAM] ตกลง API contract 7 ข้อ ก่อนเริ่มเขียนโค้ด ยัง Blocked
 *   - #50 [WEB] เข้าสู่ระบบ / ออกจากระบบ ยัง Blocked (ฝั่ง backend)
 *
 * ฟอร์มนี้เลย validate ฝั่ง client และโชว์ข้อความแจ้งสถานะไว้ก่อน
 * ห้าม hardcode localhost/IP — อ่าน API base จาก window.LUMA_CONFIG เท่านั้น
 */

const API_BASE = window.LUMA_CONFIG ? window.LUMA_CONFIG.apiBase : "";

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
      showError("กรอกอีเมลและรหัสผ่านให้ครบ");
      return;
    }

    setLoading(true);
    try {
      // TODO(#32, #50): ยังไม่มี endpoint จริง — โครงไว้รอเสียบ
      showError("ระบบ login ยังไม่เชื่อมต่อ backend (รอ issue #32/#50)");
    } catch (err) {
      showError(err.message || "เกิดข้อผิดพลาด ลองใหม่อีกครั้ง");
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
    submitBtn.textContent = isLoading ? "กำลังเข้าสู่ระบบ…" : "เข้าสู่ระบบ";
  }
}

document.addEventListener("DOMContentLoaded", initLoginForm);