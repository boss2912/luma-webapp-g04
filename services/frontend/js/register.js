/**
 * LUMA — Register form
 * -------------------------------------------------------------------------
 * ตอนนี้ใช้ js/mock-auth.js จำลอง backend ไปก่อน (ดูคอมเมนต์ในไฟล์นั้น)
 * เพราะ #32/#49 ปิด contract แล้ว แต่ backend ตัวจริงยังไม่รันขึ้นมา
 *
 * พอ backend จริงพร้อมใช้งาน ให้ลบ TODO ด้านล่างออก แล้วเรียก fetch()
 * ตรงตาม docs/API_CONTRACT.md แทน (เอา mock-auth.js ออกจาก register.html ด้วย)
 *
 * ห้าม hardcode localhost/IP — อ่าน API base จาก window.LUMA_CONFIG เท่านั้น
 *
 * หมายเหตุ: การเช็ค "อีเมลนี้มีคนใช้แล้วหรือยัง" ต้องทำที่ backend จริงเท่านั้น
 * (ดู #49 "กันการเดาว่ามีบัญชีอยู่จริง") mock-auth.js จำลองพฤติกรรมนี้ไว้แล้ว
 */

const API_BASE = window.LUMA_CONFIG ? window.LUMA_CONFIG.apiBase : "";
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
      // TODO(#49): สลับเป็น fetch จริงตอน backend รันได้แล้ว เช่น
      //
      // const res = await fetch(`${API_BASE}/api/register`, {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({ displayName, email, password }),
      // });
      // const data = await res.json();
      // if (!res.ok) throw new Error(data.message || "สมัครสมาชิกไม่สำเร็จ");

      const result = await window.LUMA_MOCK_AUTH.mockRegister({
        displayName,
        email,
        password,
      });
      if (!result.ok) {
        showError(result.data.message);
        return;
      }

      window.location.href = "login.html";
    } catch (err) {
      showError(err.message || "เกิดข้อผิดพลาด ลองใหม่อีกครั้ง");
    } finally {
      setLoading(false);
    }
  });

  /** ตรวจฝั่ง client เท่านั้น — เช็คอีเมลซ้ำต้องทำที่ backend (#49) */
  function validate({ displayName, email, password, confirmPassword }) {
    if (!displayName || !email || !password || !confirmPassword) {
      return "กรอกข้อมูลให้ครบทุกช่อง";
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
    submitBtn.textContent = isLoading ? "กำลังสมัครสมาชิก…" : "สมัครสมาชิก";
  }
}

document.addEventListener("DOMContentLoaded", initRegisterForm);