/**
 * LUMA — Register Page Logic
 * -------------------------------------------------------------------------
 * จัดการฟอร์มสมัครสมาชิก ตรวจสอบความถูกต้องของข้อมูล
 * และส่งคำขอไปยัง POST /api/auth/register
 *
 * อ้างอิง: Issue #49, docs/API_CONTRACT.md
 */

(() => {
  const API_BASE = window.LUMA_CONFIG ? window.LUMA_CONFIG.apiBase : "http://127.0.0.1:5000";

  function initRegister() {
    const form = document.getElementById("register-form");
    if (!form) return;

    const errorBox = document.getElementById("register-error");
    const successBox = document.getElementById("register-success");
    const submitBtn = document.getElementById("register-submit");

    function showError(msg) {
      if (errorBox) {
        errorBox.textContent = msg;
        errorBox.removeAttribute("hidden");
      }
      if (successBox) successBox.setAttribute("hidden", "");
    }

    function hideMessages() {
      if (errorBox) errorBox.setAttribute("hidden", "");
      if (successBox) successBox.setAttribute("hidden", "");
    }

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      hideMessages();

      const email = form.email ? form.email.value.trim() : "";
      const displayName = form.displayName ? form.displayName.value.trim() : "";
      const password = form.password ? form.password.value : "";
      const confirmPassword = form.confirmPassword ? form.confirmPassword.value : "";

      // ตรวจสอบความถูกต้องฝั่ง Client
      if (!email) {
        showError("กรุณากรอกอีเมล");
        return;
      }
      if (!email.includes("@") || !email.includes(".")) {
        showError("รูปแบบอีเมลไม่ถูกต้อง");
        return;
      }
      if (!displayName) {
        showError("กรุณากรอกชื่อแสดงผล");
        return;
      }
      if (password.length < 8) {
        showError("รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร");
        return;
      }
      if (password !== confirmPassword) {
        showError("รหัสผ่านและยืนยันรหัสผ่านไม่ตรงกัน");
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "กำลังสมัครสมาชิก…";
      }

      try {
        const res = await fetch(`${API_BASE}/api/auth/register`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            displayName,
            password,
          }),
        });

        const data = await res.json();

        if (!res.ok) {
          throw new Error(data.error || `สมัครสมาชิกไม่สำเร็จ (HTTP ${res.status})`);
        }

        if (successBox) {
          successBox.textContent = "สมัครสมาชิกสำเร็จ! กำลังนำคุณไปหน้าเข้าสู่ระบบ…";
          successBox.removeAttribute("hidden");
        }

        setTimeout(() => {
          window.location.href = "login.html?registered=true";
        }, 1500);
      } catch (err) {
        console.error("Register error:", err);
        showError(err.message || "เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = "สมัครสมาชิก";
        }
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRegister);
  } else {
    initRegister();
  }
})();