/**
 * LUMA — Register form
 * -------------------------------------------------------------------------
 * ตอนนี้ยังไม่มี endpoint จริงให้เรียก เพราะ:
 *   - #32 [TEAM] ตกลง API contract 7 ข้อ ก่อนเริ่มเขียนโค้ด ยัง Blocked
 *   - #49 [WEB] สมัครสมาชิก + ตรวจข้อมูล + กันการเดาว่ามีบัญชีอยู่จริง
 *     ยัง Blocked (ฝั่ง backend)
 *
 * หมายเหตุ: การเช็ค "อีเมลนี้มีคนใช้แล้วหรือยัง" ต้องทำที่ backend เท่านั้น
 * (ดู #49 "กันการเดาว่ามีบัญชีอยู่จริง") ฝั่ง frontend นี้เช็คได้แค่ฟอร์แมต
 * และความยาว ไม่เช็คว่าอีเมลซ้ำหรือไม่
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
      // TODO(#32, #49): ยังไม่มี endpoint จริง — โครงไว้รอเสียบ
      showError("ระบบสมัครสมาชิกยังไม่เชื่อมต่อ backend (รอ issue #32/#49)");
    } catch (err) {
      showError(err.message || "เกิดข้อผิดพลาด ลองใหม่อีกครั้ง");
    } finally {
      setLoading(false);
    }
  });

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