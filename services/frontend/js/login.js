/**
 * LUMA — Login form
 * -------------------------------------------------------------------------
 * ตอนนี้ใช้ js/mock-auth.js จำลอง backend ไปก่อน (ดูคอมเมนต์ในไฟล์นั้น)
 * เพราะ #32/#49 ปิด contract แล้ว แต่ backend ตัวจริงยังไม่รันขึ้นมา
 *
 * พอ backend จริงพร้อมใช้งาน ให้ลบ TODO ด้านล่างออก แล้วเรียก fetch()
 * ตรงตาม docs/API_CONTRACT.md แทน (เอา mock-auth.js ออกจาก login.html ด้วย)
 *
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
      // TODO(#50): สลับเป็น fetch จริงตอน backend รันได้แล้ว เช่น
      //
      // const res = await fetch(`${API_BASE}/api/login`, {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({ email, password }),
      // });
      // const data = await res.json();
      // if (!res.ok) throw new Error(data.message || "เข้าสู่ระบบไม่สำเร็จ");

      const result = await window.LUMA_MOCK_AUTH.mockLogin({
        email,
        password,
      });
      if (!result.ok) {
        showError(result.data.message);
        return;
      }

      // จำลอง session ไว้ใน sessionStorage เพื่อทดสอบ flow "จำว่าล็อกอินอยู่"
      // (ของปลอม — backend จริงจะใช้ cookie/session ฝั่งเซิร์ฟเวอร์แทน)
      sessionStorage.setItem("luma_mock_session", JSON.stringify(result.data));
      window.location.href = "index.html";
    } catch (err) {
      showError(err.message || "เกิดข้อผิดพลาด ลองใหม่อีกครั้ง");
    } finally {
      setLoading(false);
    }
  });

  function showError(message) {
    // ใช้ textContent เสมอ ไม่ใช้ innerHTML เพราะข้อความ error
    // อาจสะท้อนกลับมาจาก backend ในอนาคต ป้องกัน stored/reflected XSS
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