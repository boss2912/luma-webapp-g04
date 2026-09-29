/**
 * LUMA — ปุ่มรูปตาสลับแสดง/ซ่อนรหัสผ่าน (หน้า login และ register)
 * -------------------------------------------------------------------------
 * ใช้ร่วมกันทั้งสองหน้า — หา .auth-field__toggle ทุกตัวในหน้าแล้วผูก click เอง
 * ไม่ต้องแก้ login.js/register.js เลย เพราะแค่สลับ type ของ input ข้างๆ ปุ่ม
 */

(() => {
  function initPasswordToggles() {
    document.querySelectorAll(".auth-field__toggle").forEach((btn) => {
      const wrap = btn.closest(".auth-field__input-wrap");
      const input = wrap ? wrap.querySelector("input") : null;
      const eye = btn.querySelector(".auth-field__eye");
      const eyeOff = btn.querySelector(".auth-field__eye-off");
      if (!input) return;

      btn.addEventListener("click", () => {
        const show = input.type === "password";
        input.type = show ? "text" : "password";
        btn.setAttribute("aria-label", show ? "ซ่อนรหัสผ่าน" : "แสดงรหัสผ่าน");
        btn.setAttribute("aria-pressed", String(show));
        if (eye) eye.hidden = show;
        if (eyeOff) eyeOff.hidden = !show;
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPasswordToggles);
  } else {
    initPasswordToggles();
  }
})();
